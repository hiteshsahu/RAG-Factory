from unittest.mock import Mock, patch

import pytest
from raginator.core import Chunk, RetrievedChunk, StageError
from raginator.rerank import CrossEncoderReranker


def _candidate(chunk_id: str, content: str, rank: int) -> RetrievedChunk:
    chunk = Chunk(content=content, metadata={}, chunk_id=chunk_id, doc_id="doc")
    return RetrievedChunk(chunk=chunk, score=0.0, rank=rank)


def test_rerank_orders_by_cross_encoder_score():
    candidates = [_candidate("a", "irrelevant text", 0), _candidate("b", "relevant text", 1)]
    response = Mock(status_code=200)
    response.raise_for_status = Mock()
    response.json.return_value = [
        [{"label": "LABEL_0", "score": 0.1}],
        [{"label": "LABEL_0", "score": 0.9}],
    ]

    with patch("raginator.rerank.cross_encoder.requests.post", return_value=response) as mock_post:
        reranked = CrossEncoderReranker(api_key="test-key").rerank("query", candidates)

    assert [c.chunk.chunk_id for c in reranked] == ["b", "a"]
    assert reranked[0].rank == 0
    _, kwargs = mock_post.call_args
    assert kwargs["json"] == {"inputs": [["query", "irrelevant text"], ["query", "relevant text"]]}


def test_empty_candidates_returns_empty():
    assert CrossEncoderReranker(api_key="test-key").rerank("query", []) == []


def test_missing_api_key_raises_stage_error(monkeypatch):
    monkeypatch.delenv("RAGINATOR_HUGGINGFACE_API_KEY", raising=False)
    candidates = [_candidate("a", "text", 0)]

    with pytest.raises(StageError):
        CrossEncoderReranker().rerank("query", candidates)
