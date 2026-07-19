# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

import json
from unittest.mock import Mock, patch

from api.main import _STATE, app
from api.metrics import prometheus_observer
from fastapi.testclient import TestClient

client = TestClient(app)


def _sse_events(response_text: str) -> list[dict]:
    events = []
    for line in response_text.splitlines():
        if line.startswith("data: "):
            events.append(json.loads(line[len("data: ") :]))
    return events


def _mistral_embed_response(n: int) -> Mock:
    response = Mock(status_code=200)
    response.raise_for_status = Mock()
    response.json.return_value = {"data": [{"embedding": [0.1, 0.2, 0.3]} for _ in range(n)]}
    return response


def _mistral_chat_response(text: str) -> Mock:
    response = Mock(status_code=200)
    response.raise_for_status = Mock()
    response.json.return_value = {
        "choices": [{"message": {"content": text}}],
        "usage": {"total_tokens": 42},
    }
    return response


def _mistral_post_router(answer_text: str):
    """MistralEmbedder and MistralGenerator both do a plain `import requests`,
    so they share the exact same `requests.post` attribute -- patching it
    twice under two different module-qualified names just clobbers itself.
    One mock has to handle both endpoints, branching on the URL."""

    def respond(url: str, *args, **kwargs):
        if url.endswith("/embeddings"):
            return _mistral_embed_response(len(kwargs["json"]["input"]))
        return _mistral_chat_response(answer_text)

    return respond


def test_preflight_failed_blocks_before_any_processing(monkeypatch):
    monkeypatch.delenv("RAGINATOR_MISTRAL_API_KEY", raising=False)

    response = client.post(
        "/api/pipeline/start",
        data={"settings": json.dumps({"embedProvider": "Mistral", "llmProvider": "Mistral"})},
        files=[("files", ("doc.txt", b"hello world", "text/plain"))],
    )

    events = _sse_events(response.text)
    assert events[0]["type"] == "preflight_failed"
    assert any("RAGINATOR_MISTRAL_API_KEY" in e for e in events[0]["errors"])


def test_unsupported_file_type_is_rejected(monkeypatch):
    monkeypatch.setenv("RAGINATOR_MISTRAL_API_KEY", "test-key")

    response = client.post(
        "/api/pipeline/start",
        data={"settings": json.dumps({"embedProvider": "Mistral", "llmProvider": "Mistral"})},
        files=[("files", ("doc.exe", b"binary junk", "application/octet-stream"))],
    )

    events = _sse_events(response.text)
    assert events[0]["type"] == "error"
    assert ".exe" in events[0]["text"]


def test_root_lists_routes_and_docs_links():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()

    assert body["docs"] == {"swagger": "/docs", "redoc": "/redoc", "openapi": "/openapi.json"}

    paths = {route["path"] for route in body["routes"]}
    assert paths == {
        "/", "/api/health", "/api/pipeline/start", "/api/query", "/api/corpus/stats", "/metrics",
    }


def test_query_without_corpus_returns_409():
    _STATE["pipeline"] = None
    response = client.post("/api/query", json={"query": "anything"})
    assert response.status_code == 409


def test_corpus_stats_without_corpus_returns_404():
    _STATE["corpus_stats"] = None
    response = client.get("/api/corpus/stats")
    assert response.status_code == 404


def test_full_pipeline_run_then_query(monkeypatch, tmp_path):
    monkeypatch.setenv("RAGINATOR_MISTRAL_API_KEY", "test-key")
    _STATE["pipeline"] = None
    _STATE["corpus_stats"] = None

    index_before = prometheus_observer.registry.get_sample_value("raginator_index_requests_total") or 0
    query_before = prometheus_observer.registry.get_sample_value("raginator_query_requests_total") or 0

    settings = {
        "embedProvider": "Mistral",
        "vectorStore": "ChromaDB",
        "llmProvider": "Mistral",
        "chunkStrategy": "Fixed",
    }

    with patch("requests.post", side_effect=_mistral_post_router("unused")):
        response = client.post(
            "/api/pipeline/start",
            data={"settings": json.dumps(settings)},
            files=[("files", ("doofenshmirtz.txt", b"Behold the RAGINATOR! " * 50, "text/plain"))],
        )

    events = _sse_events(response.text)
    assert events[-1]["type"] == "complete", events
    corpus_stats = events[-1]["corpusStats"]
    assert corpus_stats["docs"] == 1
    assert corpus_stats["chunks"] > 0
    assert corpus_stats["indexSizeBytes"] > 0

    # The chat mock always answers "unused" (single line, no numbering) --
    # confirms the complete event carries whatever the generator produced.
    assert events[-1]["suggestedQuestions"] == ["unused"]

    stats_response = client.get("/api/corpus/stats")
    assert stats_response.status_code == 200
    assert stats_response.json()["docs"] == 1

    # Querying re-embeds the question (DenseRetriever) before generating.
    with patch("requests.post", side_effect=_mistral_post_router("RAGINATOR ramble.")):
        query_response = client.post("/api/query", json={"query": "What does the RAGINATOR do?"})

    assert query_response.status_code == 200
    body = query_response.json()
    assert body["answer"] == "RAGINATOR ramble."
    assert body["tokens"] == 42
    assert body["sources"]
    assert body["sources"][0]["path"]
    assert body["cost"].startswith("$")

    # The bridge bypasses Pipeline.index() (drives stages manually for SSE
    # progress), so without an explicit observer.record("indexed", ...) call
    # this would stay at 0 forever even though real uploads were happening.
    index_after = prometheus_observer.registry.get_sample_value("raginator_index_requests_total")
    query_after = prometheus_observer.registry.get_sample_value("raginator_query_requests_total")
    assert index_after == index_before + 1
    assert query_after == query_before + 1

    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    assert b"raginator_index_requests_total" in metrics_response.content


def test_full_pipeline_run_from_url_only(monkeypatch):
    monkeypatch.setenv("RAGINATOR_MISTRAL_API_KEY", "test-key")
    _STATE["pipeline"] = None
    _STATE["corpus_stats"] = None

    settings = {
        "embedProvider": "Mistral",
        "vectorStore": "ChromaDB",
        "llmProvider": "Mistral",
        "chunkStrategy": "Fixed",
    }

    web_response = Mock(text=f"<p>{'Behold the RAGINATOR! ' * 50}</p>", status_code=200)
    web_response.raise_for_status = Mock()

    with (
        patch("requests.post", side_effect=_mistral_post_router("unused")),
        patch("raginator.ingest.web.requests.get", return_value=web_response),
    ):
        response = client.post(
            "/api/pipeline/start",
            data={"settings": json.dumps(settings), "urls": ["https://example.com"]},
        )

    events = _sse_events(response.text)
    assert events[-1]["type"] == "complete", events
    assert events[-1]["corpusStats"]["docs"] == 1


def test_full_pipeline_run_from_pasted_text_only(monkeypatch):
    monkeypatch.setenv("RAGINATOR_MISTRAL_API_KEY", "test-key")
    _STATE["pipeline"] = None
    _STATE["corpus_stats"] = None

    settings = {
        "embedProvider": "Mistral",
        "vectorStore": "ChromaDB",
        "llmProvider": "Mistral",
        "chunkStrategy": "Fixed",
    }

    with patch("requests.post", side_effect=_mistral_post_router("unused")):
        response = client.post(
            "/api/pipeline/start",
            data={"settings": json.dumps(settings), "texts": ["Behold the RAGINATOR! " * 50]},
        )

    events = _sse_events(response.text)
    assert events[-1]["type"] == "complete", events
    assert events[-1]["corpusStats"]["docs"] == 1
