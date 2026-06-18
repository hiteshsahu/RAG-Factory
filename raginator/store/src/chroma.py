from __future__ import annotations

from typing import Any

import chromadb
from raginator.core import Chunk, EmbeddedChunk, RetrievedChunk, VectorStore


class ChromaVectorStore(VectorStore):
    """Vector store backed by ChromaDB (The Store-Inator, default -- zero config).

    Runs fully in-process with no external service; pass persist_directory to
    keep data on disk across runs instead of the default in-memory client.
    """

    def __init__(
        self,
        collection_name: str = "raginator",
        persist_directory: str | None = None,
        client: Any | None = None,
    ) -> None:
        if client is not None:
            self._client = client
        elif persist_directory is not None:
            self._client = chromadb.PersistentClient(path=persist_directory)
        else:
            self._client = chromadb.Client()
        self._collection = self._client.get_or_create_collection(name=collection_name)

    def add(self, embedded_chunk: EmbeddedChunk) -> None:
        chunk = embedded_chunk.chunk
        self._collection.add(
            ids=[chunk.chunk_id],
            embeddings=[embedded_chunk.embedding],
            documents=[chunk.content],
            metadatas=[{"doc_id": chunk.doc_id, **chunk.metadata}],
        )

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[RetrievedChunk]:
        results = self._collection.query(query_embeddings=[query_embedding], n_results=top_k)

        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        retrieved = []
        for rank, (chunk_id, content, metadata, distance) in enumerate(
            zip(ids, documents, metadatas, distances, strict=True)
        ):
            metadata = dict(metadata)
            doc_id = metadata.pop("doc_id", "")
            chunk = Chunk(content=content, metadata=metadata, chunk_id=chunk_id, doc_id=doc_id)
            retrieved.append(RetrievedChunk(chunk=chunk, score=1.0 - distance, rank=rank))
        return retrieved
