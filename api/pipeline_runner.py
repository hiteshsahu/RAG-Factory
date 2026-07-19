# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import shutil
import tempfile
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

from api import providers
from api.metrics import bridge_observer
from api.schemas import EMBED_MODELS, CorpusStats, PipelineSettings
from raginator.core import Chunk, Generator, RetrievedChunk
from raginator.evaluate import KeywordOverlapEvaluator
from raginator.ingest import PDFIngestor, TextFileIngestor
from raginator.pipeline import Pipeline
from raginator.rerank import IdentityReranker
from raginator.retrieve import DenseRetriever

UNSUPPORTED_EXTENSIONS = {".docx"}
# TextFileIngestor only globs *.txt -- markdown is text too, just saved under
# the extension it'll actually be picked up under.
TEXT_LIKE_EXTENSIONS = {".txt", ".md"}

# Stages 4-7 (Retrieve/Rerank/Generate/Evaluate) don't run during indexing in
# the real Pipeline -- Pipeline.index() only touches ingest/chunk/embed/store.
# We still construct the real provider objects for them here (so a bad API
# key/model surfaces immediately), we just don't have a query to run yet.
_WARMUP_STAGES = ((4, "Retriever"), (5, "Reranker"), (6, "Generator"), (7, "Evaluator"))

# Generator.generate() only takes a (query, context) pair -- there's no raw
# "complete this prompt" method on the interface -- so suggestion generation
# reuses it by treating the instruction itself as the "query" and a sample of
# the corpus as "context". A handful of chunks is plenty signal for 3 questions
# and keeps this cheap regardless of corpus size.
_SUGGESTION_SAMPLE_SIZE = 6
_SUGGESTION_PROMPT = (
    "Suggest exactly 3 short, specific questions a reader could ask about the "
    "document above. Reply with ONLY the 3 questions, one per line -- no "
    "numbering, no bullets, no extra commentary."
)


def _suggest_questions(generator: Generator, chunks: list[Chunk]) -> list[str]:
    sample = chunks[:_SUGGESTION_SAMPLE_SIZE]
    context = [RetrievedChunk(chunk=c, score=1.0, rank=i) for i, c in enumerate(sample)]
    answer = generator.generate(_SUGGESTION_PROMPT, context)
    questions = [line.strip().lstrip("-*•0123456789.) ").strip() for line in answer.answer.splitlines()]
    return [q for q in questions if q][:3]


async def run_pipeline(
    files: list[tuple[str, bytes]],
    settings: PipelineSettings,
    state: dict[str, Any],
) -> AsyncIterator[dict[str, Any]]:
    """Drives ingest->chunk->embed->store stage by stage (rather than calling
    the opaque Pipeline.index() in one shot) so each stage can emit its own
    progress event and so a failure can be attributed to the stage that broke.
    On success, stores the constructed Pipeline + CorpusStats into `state`.
    """
    unsupported = [name for name, _ in files if Path(name).suffix.lower() in UNSUPPORTED_EXTENSIONS]
    if unsupported:
        yield {
            "type": "error",
            "stage": -1,
            "text": f"Unsupported file type(s): {', '.join(unsupported)} "
            "-- no ingest stage handles .docx yet. Use PDF, TXT, or MD.",
        }
        return

    tmp_dir = Path(tempfile.mkdtemp(prefix="raginator-"))
    try:
        for name, content in files:
            dest = tmp_dir / name
            if dest.suffix.lower() in TEXT_LIKE_EXTENSIONS:
                dest = dest.with_suffix(".txt")
            dest.write_bytes(content)

        try:
            embedder = providers.build_embedder(settings.embed_provider)
            chunker = providers.build_chunker(settings.chunk_strategy, embedder)
            store = providers.build_store(settings.vector_store)
        except Exception as exc:
            yield {"type": "error", "stage": 2, "text": str(exc)}
            return

        # Stage 0 -- Ingest
        try:
            documents = [
                *TextFileIngestor(tmp_dir).ingest(),
                *PDFIngestor(tmp_dir).ingest(),
            ]
        except Exception as exc:
            yield {"type": "error", "stage": 0, "text": str(exc)}
            return
        if not documents:
            yield {"type": "error", "stage": 0, "text": "No ingestable documents found in the upload"}
            return
        yield {"type": "log", "stage": 0, "text": f"Loaded {len(documents)} document(s)", "kind": "default"}
        yield {"type": "stage_done", "stage": 0, "stat": f"{len(documents)} docs"}

        # Stage 1 -- Chunk
        try:
            all_chunks: list[Chunk] = []
            for document in documents:
                all_chunks.extend(chunker.chunk(document))
        except Exception as exc:
            yield {"type": "error", "stage": 1, "text": str(exc)}
            return
        if not all_chunks:
            yield {"type": "error", "stage": 1, "text": "Chunker produced zero chunks from the upload"}
            return
        yield {
            "type": "log", "stage": 1,
            "text": f"{len(documents)} docs -> {len(all_chunks)} chunks ({settings.chunk_strategy})",
            "kind": "default",
        }
        yield {"type": "stage_done", "stage": 1, "stat": f"{len(all_chunks):,} chunks"}

        retriever = DenseRetriever(embedder, store)
        retriever.index(all_chunks)

        # Stage 2 -- Embed
        try:
            embedded = embedder.embed_chunks(all_chunks)
        except Exception as exc:
            yield {"type": "error", "stage": 2, "text": str(exc)}
            return
        dim = len(embedded[0].embedding) if embedded else 0
        yield {
            "type": "log", "stage": 2,
            "text": f"Embedded {len(embedded)} chunks via {settings.embed_provider} ({EMBED_MODELS[settings.embed_provider]})",
            "kind": "default",
        }
        yield {"type": "stage_done", "stage": 2, "stat": f"dim={dim} · {settings.embed_provider}"}

        # Stage 3 -- Store
        try:
            for embedded_chunk in embedded:
                store.add(embedded_chunk)
        except Exception as exc:
            yield {"type": "error", "stage": 3, "text": str(exc)}
            return
        yield {
            "type": "log", "stage": 3,
            "text": f"{len(embedded)} vectors persisted to {settings.vector_store}",
            "kind": "default",
        }
        yield {"type": "stage_done", "stage": 3, "stat": f"{settings.vector_store} · {len(embedded):,} vectors"}

        # Stages 4-7 -- construct + ready the query-time components.
        try:
            generator = providers.build_generator(settings.llm_provider)
            reranker = IdentityReranker()
            evaluator = KeywordOverlapEvaluator()
        except Exception as exc:
            yield {"type": "error", "stage": 6, "text": str(exc)}
            return
        for stage_num, label in _WARMUP_STAGES:
            yield {"type": "log", "stage": stage_num, "text": f"{label} ready", "kind": "default"}
            yield {"type": "stage_done", "stage": stage_num, "stat": "ready"}

        # Pipeline.index() is what normally fires the "indexed" observer
        # event, but the bridge drives ingest/chunk/embed/store manually
        # above (for per-stage SSE progress) instead of calling it -- so
        # without this, real uploads through the UI would never show up in
        # Prometheus/Grafana at all, only the unrelated `./go metrics_server`
        # toy demo loop would.
        observer = bridge_observer()
        observer.record("indexed", chunk_count=len(all_chunks))

        pipeline = Pipeline(
            ingestor=TextFileIngestor(tmp_dir),
            chunker=chunker,
            embedder=embedder,
            store=store,
            retriever=retriever,
            reranker=reranker,
            generator=generator,
            evaluator=evaluator,
            observer=observer,
        )

        avg_chunk_tokens = (
            round(sum(len(c.content.split()) for c in all_chunks) / len(all_chunks)) if all_chunks else 0
        )
        corpus_stats = CorpusStats(
            docs=len(documents),
            chunks=len(all_chunks),
            avg_chunk_tokens=avg_chunk_tokens,
            embedding_model=f"{EMBED_MODELS[settings.embed_provider]} · {dim}-dim",
            index_size_bytes=len(all_chunks) * dim * 4,  # float32 vectors
        )

        state["pipeline"] = pipeline
        state["settings"] = settings
        state["corpus_stats"] = corpus_stats

        # Best-effort: a flaky suggestion call shouldn't fail an otherwise
        # successfully indexed corpus -- just fall back to no suggestions
        # (the UI falls back to its own canned chips when this is empty).
        suggested_questions: list[str] = []
        try:
            yield {"type": "log", "stage": 6, "text": "Generating question suggestions...", "kind": "default"}
            suggested_questions = _suggest_questions(generator, all_chunks)
        except Exception as exc:
            yield {"type": "log", "stage": 6, "text": f"Suggestion generation skipped: {exc}", "kind": "error"}

        yield {
            "type": "complete",
            "corpusStats": corpus_stats.model_dump(by_alias=True),
            "suggestedQuestions": suggested_questions,
        }
    except Exception as exc:  # belt-and-suspenders: never let the stream die silently
        yield {"type": "error", "stage": -1, "text": f"Unexpected error: {exc}"}
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
