from __future__ import annotations

import numpy as np
from ragfactory.core import EmbeddedChunk, RetrievedChunk, VectorStore

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
    """Holds embedded chunks in memory; scores via the native extension when available (The Store-Inator)."""

    def __init__(self) -> None:
        self._embedded_chunks: list[EmbeddedChunk] = []
        self._vectors: list[np.ndarray] = []

    def add(self, embedded_chunk: EmbeddedChunk) -> None:
        self._embedded_chunks.append(embedded_chunk)
        self._vectors.append(np.asarray(embedded_chunk.embedding, dtype=np.float32))

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[RetrievedChunk]:
        if not self._vectors:
            return []
        candidates = np.stack(self._vectors)
        scores = _cosine_similarity_batch(np.asarray(query_embedding, dtype=np.float32), candidates)
        ranked = sorted(
            zip(self._embedded_chunks, scores, strict=True),
            key=lambda pair: pair[1],
            reverse=True,
        )
        return [
            RetrievedChunk(chunk=embedded.chunk, score=float(score), rank=rank)
            for rank, (embedded, score) in enumerate(ranked[:top_k])
        ]
