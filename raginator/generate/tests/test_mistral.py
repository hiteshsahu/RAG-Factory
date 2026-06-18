from unittest.mock import Mock, patch

import pytest
from raginator.core import Chunk, RetrievedChunk, StageError
from raginator.generate import MistralGenerator


def _context(text: str) -> RetrievedChunk:
    chunk = Chunk(content=text, metadata={}, chunk_id="c", doc_id="d")
    return RetrievedChunk(chunk=chunk, score=1.0, rank=0)


def test_generate_calls_mistral_chat_api():
    response = Mock(status_code=200)
    response.raise_for_status = Mock()
    response.json.return_value = {
        "choices": [{"message": {"content": "Doofenshmirtz built it."}}],
        "usage": {"total_tokens": 42},
    }

    with patch("raginator.generate.mistral.requests.post", return_value=response) as mock_post:
        answer = MistralGenerator(api_key="test-key").generate(
            "Who built it?", [_context("Doofenshmirtz built the Raginator.")]
        )

    assert answer.answer == "Doofenshmirtz built it."
    assert answer.sources[0].chunk.content == "Doofenshmirtz built the Raginator."
    assert answer.tokens_used == 42
    assert answer.latency_ms >= 0
    _, kwargs = mock_post.call_args
    assert kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert kwargs["json"]["model"] == "mistral-small-latest"
    assert "Doofenshmirtz built the Raginator." in kwargs["json"]["messages"][1]["content"]


def test_missing_api_key_raises_stage_error(monkeypatch):
    monkeypatch.delenv("RAGINATOR_MISTRAL_API_KEY", raising=False)

    with pytest.raises(StageError):
        MistralGenerator().generate("question", [])
