from raginator.core import Chunk, RetrievedChunk
from raginator.rerank import IdentityReranker


def test_identity_reranker_preserves_order():
    chunk_a = Chunk(content="a", metadata={}, chunk_id="a", doc_id="d")
    chunk_b = Chunk(content="b", metadata={}, chunk_id="b", doc_id="d")
    candidates = [
        RetrievedChunk(chunk=chunk_a, score=0.9, rank=0),
        RetrievedChunk(chunk=chunk_b, score=0.5, rank=1),
    ]

    assert IdentityReranker().rerank("query", candidates) == candidates
