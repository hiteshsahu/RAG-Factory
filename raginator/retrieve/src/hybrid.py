from __future__ import annotations

from raginator.core import Chunk, RetrievedChunk, Retriever

from .dense import DenseRetriever
from .sparse import SparseRetriever


class HybridRetriever(Retriever):
    """Combines dense (embedding) and sparse (BM25) retrieval scores
    (The Find-Inator, hybrid mode).

    Each side's scores are min-max normalized to [0, 1] independently, then
    combined as alpha * dense + (1 - alpha) * sparse.
    """

    def __init__(
        self, dense: DenseRetriever, sparse: SparseRetriever, alpha: float = 0.5
    ) -> None:
        self._dense = dense
        self._sparse = sparse
        self._alpha = alpha

    def index(self, chunks: list[Chunk]) -> None:
        self._sparse.index(chunks)

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        fetch_k = max(top_k * 2, top_k)
        dense_results = self._dense.retrieve(query, top_k=fetch_k)
        sparse_results = self._sparse.retrieve(query, top_k=fetch_k)

        dense_scores = _normalize({r.chunk.chunk_id: r.score for r in dense_results})
        sparse_scores = _normalize({r.chunk.chunk_id: r.score for r in sparse_results})
        chunks_by_id = {r.chunk.chunk_id: r.chunk for r in (*dense_results, *sparse_results)}

        combined = {
            chunk_id: self._alpha * dense_scores.get(chunk_id, 0.0)
            + (1 - self._alpha) * sparse_scores.get(chunk_id, 0.0)
            for chunk_id in chunks_by_id
        }
        ranked_ids = sorted(combined, key=lambda chunk_id: combined[chunk_id], reverse=True)[
            :top_k
        ]
        return [
            RetrievedChunk(chunk=chunks_by_id[chunk_id], score=combined[chunk_id], rank=rank)
            for rank, chunk_id in enumerate(ranked_ids)
        ]


def _normalize(scores: dict[str, float]) -> dict[str, float]:
    if not scores:
        return {}
    values = scores.values()
    lo, hi = min(values), max(values)
    if hi == lo:
        return dict.fromkeys(scores, 1.0)
    return {key: (value - lo) / (hi - lo) for key, value in scores.items()}
