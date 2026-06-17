from __future__ import annotations

from ragfactory.core import Reranker


class IdentityReranker(Reranker):
    """Keeps retrieval order as-is (The Better-Find-Inator).

    Placeholder for a real cross-encoder reranker.
    """

    def rerank(
        self, query: str, candidates: list[tuple[str, float]]
    ) -> list[tuple[str, float]]:
        return candidates
