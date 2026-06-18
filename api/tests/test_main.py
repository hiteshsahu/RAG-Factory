import json
from unittest.mock import Mock, patch

from api.main import _STATE, app
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
        files=[("files", ("doc.docx", b"binary junk", "application/msword"))],
    )

    events = _sse_events(response.text)
    assert events[0]["type"] == "error"
    assert ".docx" in events[0]["text"]


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
