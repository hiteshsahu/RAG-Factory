from __future__ import annotations

from raginator.core import Reranker, RetrievedChunk


class IdentityReranker(Reranker):
    """Keeps retrieval order as-is (The Better-Find-Inator).

    Placeholder for a real cross-encoder reranker.
    """

    def rerank(
        self, query: str, candidates: list[RetrievedChunk]
    ) -> list[RetrievedChunk]:
        return candidates
