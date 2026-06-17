from ragfactory.core import Chunk, RetrievedChunk
from ragfactory.evaluate import mean_reciprocal_rank, precision_at_k, recall_at_k, retrieval_metrics


def _retrieved(*chunk_ids: str) -> list[RetrievedChunk]:
    return [
        RetrievedChunk(
            chunk=Chunk(content="x", metadata={}, chunk_id=chunk_id, doc_id="d"),
            score=1.0,
            rank=index,
        )
        for index, chunk_id in enumerate(chunk_ids)
    ]


def test_precision_at_k():
    retrieved = _retrieved("a", "b", "c", "d")
    assert precision_at_k(retrieved, {"a", "c"}, k=4) == 0.5
    assert precision_at_k(retrieved, {"a", "c"}, k=2) == 0.5


def test_recall_at_k():
    retrieved = _retrieved("a", "b", "c")
    assert recall_at_k(retrieved, {"a", "c", "z"}, k=3) == 2 / 3


def test_mean_reciprocal_rank():
    retrieved = _retrieved("a", "b", "c")
    assert mean_reciprocal_rank(retrieved, {"b"}) == 0.5
    assert mean_reciprocal_rank(retrieved, {"z"}) == 0.0


def test_empty_inputs_return_zero():
    assert precision_at_k([], {"a"}, k=5) == 0.0
    assert recall_at_k(_retrieved("a"), set(), k=5) == 0.0


def test_retrieval_metrics_bundle():
    retrieved = _retrieved("a", "b")
    metrics = retrieval_metrics(retrieved, {"a"}, k=2)
    assert set(metrics) == {"precision_at_k", "recall_at_k", "mrr"}
