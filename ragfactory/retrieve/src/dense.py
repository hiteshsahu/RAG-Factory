from __future__ import annotations

from ragfactory.core import Embedder, RetrievedChunk, Retriever, VectorStore


class DenseRetriever(Retriever):
    """Embeds the query and looks up the closest vectors in the store (The Find-Inator, dense mode)."""

    def __init__(self, embedder: Embedder, store: VectorStore) -> None:
        self._embedder = embedder
        self._store = store

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        [query_embedding] = self._embedder.embed_texts([query])
        return self._store.search(query_embedding, top_k=top_k)
