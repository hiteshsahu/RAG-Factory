from __future__ import annotations

from raginator.core import RetrievedChunk


def precision_at_k(retrieved: list[RetrievedChunk], relevant_ids: set[str], k: int) -> float:
    """Fraction of the top-k retrieved chunks that are actually relevant."""
    top_k = retrieved[:k]
    if not top_k:
        return 0.0
    return sum(1 for result in top_k if result.chunk.chunk_id in relevant_ids) / len(top_k)


def recall_at_k(retrieved: list[RetrievedChunk], relevant_ids: set[str], k: int) -> float:
    """Fraction of all relevant chunks that appear in the top-k retrieved."""
    if not relevant_ids:
        return 0.0
    top_k = retrieved[:k]
    found = sum(1 for result in top_k if result.chunk.chunk_id in relevant_ids)
    return found / len(relevant_ids)


def mean_reciprocal_rank(retrieved: list[RetrievedChunk], relevant_ids: set[str]) -> float:
    """1 / rank of the first relevant chunk, or 0.0 if none of the retrieved chunks are relevant."""
    for rank, result in enumerate(retrieved, start=1):
        if result.chunk.chunk_id in relevant_ids:
            return 1.0 / rank
    return 0.0


def retrieval_metrics(
    retrieved: list[RetrievedChunk], relevant_ids: set[str], k: int = 5
) -> dict[str, float]:
    """Bundles all three retrieval metrics together, e.g. for report.py."""
    return {
        "precision_at_k": precision_at_k(retrieved, relevant_ids, k),
        "recall_at_k": recall_at_k(retrieved, relevant_ids, k),
        "mrr": mean_reciprocal_rank(retrieved, relevant_ids),
    }
