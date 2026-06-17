from unittest.mock import Mock, patch

import pytest
from ragfactory.core import Chunk, RetrievedChunk, StageError
from ragfactory.generate import OpenAIGenerator


def _context(text: str) -> RetrievedChunk:
    chunk = Chunk(content=text, metadata={}, chunk_id="c", doc_id="d")
    return RetrievedChunk(chunk=chunk, score=1.0, rank=0)


def test_generate_calls_openai_chat_api():
    response = Mock(status_code=200)
    response.raise_for_status = Mock()
    response.json.return_value = {
        "choices": [{"message": {"content": "It's a RAG machine."}}],
        "usage": {"total_tokens": 17},
    }

    with patch("ragfactory.generate.openai.requests.post", return_value=response) as mock_post:
        answer = OpenAIGenerator(api_key="test-key").generate(
            "What is it?", [_context("The RAGINATOR is a RAG machine.")]
        )

    assert answer.answer == "It's a RAG machine."
    assert answer.tokens_used == 17
    _, kwargs = mock_post.call_args
    assert kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert kwargs["json"]["model"] == "gpt-4o-mini"


def test_generate_without_context_skips_context_block():
    response = Mock(status_code=200)
    response.raise_for_status = Mock()
    response.json.return_value = {"choices": [{"message": {"content": "I don't know."}}]}

    with patch("ragfactory.generate.openai.requests.post", return_value=response) as mock_post:
        OpenAIGenerator(api_key="test-key").generate("unanswerable", [])

    _, kwargs = mock_post.call_args
    assert "No context was retrieved" in kwargs["json"]["messages"][1]["content"]


def test_missing_api_key_raises_stage_error(monkeypatch):
    monkeypatch.delenv("RAGFACTORY_OPENAI_API_KEY", raising=False)

    with pytest.raises(StageError):
        OpenAIGenerator().generate("question", [])
