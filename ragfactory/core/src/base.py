from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any

from .types import Chunk, EmbeddedChunk, GeneratedAnswer, RawDocument, RetrievedChunk


class Ingestor(ABC):
    """Stage 0 — pulls raw documents from a source."""

    @abstractmethod
    def ingest(self) -> Iterable[RawDocument]: ...


class Chunker(ABC):
    """Stage 1 — splits a document into retrievable chunks."""

    @abstractmethod
    def chunk(self, document: RawDocument) -> list[Chunk]: ...


class Embedder(ABC):
    """Stage 2 — converts text into vector embeddings."""

    provider_name: str = "unknown"

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...

    def embed_chunks(self, chunks: list[Chunk]) -> list[EmbeddedChunk]:
        """Convenience wrapper used by the indexing flow (Stage 2 -> Stage 3).

        Query embedding (Stage 4) calls embed_texts directly instead, since a
        query string isn't a document Chunk.
        """
        vectors = self.embed_texts([chunk.content for chunk in chunks])
        return [
            EmbeddedChunk(chunk=chunk, embedding=vector, provider=self.provider_name)
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]


class VectorStore(ABC):
    """Stage 3 — persists embedded chunks for later similarity search."""

    @abstractmethod
    def add(self, embedded_chunk: EmbeddedChunk) -> None: ...

    @abstractmethod
    def search(self, query_embedding: list[float], top_k: int) -> list[RetrievedChunk]: ...


class Retriever(ABC):
    """Stage 4 — finds candidate chunks relevant to a query."""

    @abstractmethod
    def retrieve(self, query: str, top_k: int) -> list[RetrievedChunk]: ...


class Reranker(ABC):
    """Stage 5 — reorders retrieved candidates by relevance."""

    @abstractmethod
    def rerank(
        self, query: str, candidates: list[RetrievedChunk]
    ) -> list[RetrievedChunk]: ...


class Generator(ABC):
    """Stage 6 — produces a final answer from a query and its context."""

    @abstractmethod
    def generate(self, query: str, context: list[RetrievedChunk]) -> GeneratedAnswer: ...


class Evaluator(ABC):
    """Stage 7 — scores the quality of a generated answer."""

    @abstractmethod
    def evaluate(
        self, query: str, answer: GeneratedAnswer, context: list[RetrievedChunk]
    ) -> float: ...


class Observer(ABC):
    """Stage 8 — records pipeline events for monitoring."""

    @abstractmethod
    def record(self, event: str, **data: Any) -> None: ...
