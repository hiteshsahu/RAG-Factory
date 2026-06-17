from __future__ import annotations

import numpy as np
from ragfactory.core import VectorStore

try:
    import ragfactory_native as _native
except ImportError:
    _native = None


def _cosine_similarity_batch(query: np.ndarray, candidates: np.ndarray) -> np.ndarray:
    """Routes through the native CPU/CUDA extension when built, else falls back to numpy."""
    if _native is not None:
        return np.asarray(
            _native.cosine_similarity_batch(query.tolist(), candidates.tolist()),
            dtype=np.float32,
        )
    query_norm = np.linalg.norm(query)
    candidate_norms = np.linalg.norm(candidates, axis=1)
    dots = candidates @ query
    denom = np.where(candidate_norms * query_norm > 0, candidate_norms * query_norm, 1.0)
    return dots / denom


class InMemoryVectorStore(VectorStore):
    """Holds embeddings in memory; scores via the native extension when available (The Store-Inator)."""

    def __init__(self) -> None:
        self._ids: list[str] = []
        self._vectors: list[np.ndarray] = []

    def add(self, doc_id: str, vector: np.ndarray) -> None:
        self._ids.append(doc_id)
        self._vectors.append(np.asarray(vector, dtype=np.float32))

    def search(self, query: np.ndarray, top_k: int = 5) -> list[tuple[str, float]]:
        if not self._vectors:
            return []
        candidates = np.stack(self._vectors)
        scores = _cosine_similarity_batch(np.asarray(query, dtype=np.float32), candidates)
        ranked = sorted(zip(self._ids, scores, strict=True), key=lambda pair: pair[1], reverse=True)
        return [(doc_id, float(score)) for doc_id, score in ranked[:top_k]]
