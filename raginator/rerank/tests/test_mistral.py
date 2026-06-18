from unittest.mock import Mock, patch

import pytest
from raginator.core import Chunk, RetrievedChunk, StageError
from raginator.rerank import MistralReranker


def _candidate(chunk_id: str, content: str, rank: int) -> RetrievedChunk:
    chunk = Chunk(content=content, metadata={}, chunk_id=chunk_id, doc_id="doc")
    return RetrievedChunk(chunk=chunk, score=0.0, rank=rank)


def test_rerank_orders_by_relevance_score():
    candidates = [_candidate("a", "irrelevant text", 0), _candidate("b", "relevant text", 1)]
    response = Mock(status_code=200)
    response.raise_for_status = Mock()
    response.json.return_value = {
        "results": [
            {"index": 0, "relevance_score": 0.2},
            {"index": 1, "relevance_score": 0.95},
        ]
    }

    with patch("raginator.rerank.mistral.requests.post", return_value=response) as mock_post:
        reranked = MistralReranker(api_key="test-key").rerank("query", candidates)

    assert [c.chunk.chunk_id for c in reranked] == ["b", "a"]
    assert reranked[0].score == 0.95
    assert reranked[0].rank == 0
    _, kwargs = mock_post.call_args
    assert kwargs["json"]["documents"] == ["irrelevant text", "relevant text"]
    assert kwargs["json"]["top_n"] == 2


def test_empty_candidates_returns_empty():
    assert MistralReranker(api_key="test-key").rerank("query", []) == []


def test_missing_api_key_raises_stage_error(monkeypatch):
    monkeypatch.delenv("RAGINATOR_MISTRAL_API_KEY", raising=False)
    candidates = [_candidate("a", "text", 0)]

    with pytest.raises(StageError):
        MistralReranker().rerank("query", candidates)
