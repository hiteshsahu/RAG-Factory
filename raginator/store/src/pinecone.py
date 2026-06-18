from __future__ import annotations

from typing import Any

from pinecone import Pinecone
from raginator.core import Chunk, EmbeddedChunk, RetrievedChunk, Settings, StageError, VectorStore


class PineconeVectorStore(VectorStore):
    """Vector store backed by Pinecone, a managed cloud vector database (The Store-Inator)."""

    def __init__(
        self,
        index_name: str,
        api_key: str | None = None,
        index: Any | None = None,
    ) -> None:
        self._index_name = index_name
        if index is not None:
            self._index = index
            return

        resolved_key = api_key if api_key is not None else Settings().pinecone_api_key
        if not resolved_key:
            raise StageError(
                "store", "Pinecone API key not set (pass api_key= or set RAGINATOR_PINECONE_API_KEY)"
            )
        self._index = Pinecone(api_key=resolved_key).Index(index_name)

    def add(self, embedded_chunk: EmbeddedChunk) -> None:
        chunk = embedded_chunk.chunk
        self._index.upsert(
            vectors=[
                {
                    "id": chunk.chunk_id,
                    "values": embedded_chunk.embedding,
                    "metadata": {
                        "doc_id": chunk.doc_id,
                        "content": chunk.content,
                        **chunk.metadata,
                    },
                }
            ]
        )

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[RetrievedChunk]:
        results = self._index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

        retrieved = []
        for rank, match in enumerate(results["matches"]):
            metadata = dict(match["metadata"])
            doc_id = metadata.pop("doc_id", "")
            content = metadata.pop("content", "")
            chunk = Chunk(content=content, metadata=metadata, chunk_id=match["id"], doc_id=doc_id)
            retrieved.append(RetrievedChunk(chunk=chunk, score=float(match["score"]), rank=rank))
        return retrieved
