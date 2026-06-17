from __future__ import annotations

from ragfactory.core import Embedder, Retriever, VectorStore


class TopKRetriever(Retriever):
    """Embeds the query and looks up the closest vectors in the store (The Find-Inator)."""

    def __init__(self, embedder: Embedder, store: VectorStore) -> None:
        self._embedder = embedder
        self._store = store

    def retrieve(self, query: str, top_k: int = 5) -> list[tuple[str, float]]:
        [query_vector] = self._embedder.embed([query])
        return self._store.search(query_vector, top_k=top_k)
