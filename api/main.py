# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any

from api.metrics import prometheus_observer
from api.pipeline_runner import run_pipeline
from api.preflight import preflight
from api.schemas import (
    LLM_MODELS,
    CorpusStats,
    PipelineSettings,
    QueryRequest,
    QueryResponse,
    SourceChunk,
)
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from fastapi.routing import APIRoute
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from raginator.core import StageError

app = FastAPI(title="Raginator bridge")

# Vite's dev server -- 5173 is the default port, 5174 is what it falls back
# to when 5173 is already taken (see frontend/README.md).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single global in-memory session -- this bridge (like the UI) only ever
# tracks one corpus at a time, matching DropState/ProcessState/ChatState's
# single-pipeline assumption.
_STATE: dict[str, Any] = {"pipeline": None, "settings": None, "corpus_stats": None}


def _sse(event: dict[str, Any]) -> str:
    return f"data: {json.dumps(event)}\n\n"


@app.get("/")
async def root() -> dict[str, Any]:
    """Lists every registered route -- read from app.routes itself (not a
    hardcoded list) so it can't drift out of sync as endpoints are added.
    Swagger/ReDoc/OpenAPI aren't APIRoute instances (FastAPI wires them up as
    plain Starlette routes), so they're surfaced separately via app.*_url."""
    routes: list[dict[str, Any]] = [
        {"path": route.path, "methods": sorted(route.methods or [])}
        for route in app.routes
        if isinstance(route, APIRoute)
    ]
    routes.sort(key=lambda r: str(r["path"]))
    return {
        "docs": {"swagger": app.docs_url, "redoc": app.redoc_url, "openapi": app.openapi_url},
        "routes": routes,
    }


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> Response:
    """Real bridge usage (uploads, queries) as Prometheus counters -- add
    this bridge as its own scrape target (see docker/prometheus.yml) to see
    actual UI activity in Grafana, not just `./go metrics_server`'s toy demo
    loop on :8000."""
    return Response(generate_latest(prometheus_observer.registry), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/pipeline/start")
async def start_pipeline(
    files: list[UploadFile] | None = File(default=None),
    urls: list[str] | None = Form(default=None),
    texts: list[str] | None = Form(default=None),
    settings: str = Form(...),
) -> StreamingResponse:
    """Runs the real pipeline over the uploaded files + URLs + pasted text and
    streams progress as SSE events: {type: log|stage_done|error|complete, ...}.
    Multipart file upload + a streamed SSE response can't go through a plain
    EventSource (browsers only let EventSource issue GET) -- the frontend
    reads this with fetch() + a manual stream reader instead."""
    parsed_settings = PipelineSettings.model_validate_json(settings)

    errors = preflight(parsed_settings)
    if errors:
        async def preflight_failed() -> AsyncIterator[str]:
            yield _sse({"type": "preflight_failed", "errors": errors})

        return StreamingResponse(preflight_failed(), media_type="text/event-stream")

    file_payload = [(f.filename or "upload", await f.read()) for f in files or []]

    async def event_stream() -> AsyncIterator[str]:
        async for event in run_pipeline(file_payload, urls or [], texts or [], parsed_settings, _STATE):
            yield _sse(event)
            # run_pipeline's stages are blocking sync calls with no `await`
            # between yields, so the event loop never gets a turn to actually
            # flush the previous chunk to the socket before the next (often
            # multi-second) stage starts -- every event ends up arriving in
            # one final burst instead of incrementally. This forces a real
            # checkpoint so the client sees each stage as it actually finishes.
            await asyncio.sleep(0)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/api/query")
async def query(request: QueryRequest) -> QueryResponse:
    pipeline = _STATE.get("pipeline")
    settings: PipelineSettings | None = _STATE.get("settings")
    if pipeline is None or settings is None:
        raise HTTPException(status_code=409, detail="No corpus indexed yet -- run /api/pipeline/start first")

    answer = pipeline.query(request.query)

    cost_usd = 0.0
    if settings.llm_provider != "Ollama":
        try:
            from raginator.evaluate import cost_per_query

            cost_usd = cost_per_query(answer, LLM_MODELS[settings.llm_provider])
        except StageError:
            pass  # no pricing entry -- leave at $0 rather than fail the query

    sources = [
        SourceChunk(
            path=retrieved.chunk.metadata.get("path", retrieved.chunk.doc_id),
            text=retrieved.chunk.content,
            score=retrieved.score,
        )
        for retrieved in answer.sources
    ]
    return QueryResponse(
        answer=answer.answer,
        sources=sources,
        ms=answer.latency_ms,
        tokens=answer.tokens_used,
        cost=f"${cost_usd:.5f}",
    )


@app.get("/api/corpus/stats")
async def corpus_stats() -> CorpusStats:
    stats = _STATE.get("corpus_stats")
    if stats is None:
        raise HTTPException(status_code=404, detail="No corpus indexed yet -- run /api/pipeline/start first")
    return stats
