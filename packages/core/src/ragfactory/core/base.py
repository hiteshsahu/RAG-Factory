from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable


class Ingestor(ABC):
    """Stage 0 — pulls raw documents from a source into plain text."""

    @abstractmethod
    def ingest(self) -> Iterable[str]: ...


class Chunker(ABC):
    """Stage 1 — splits a document into retrievable chunks."""

    @abstractmethod
    def chunk(self, text: str) -> list[str]: ...


class Embedder(ABC):
    """Stage 2 — converts chunks into vector embeddings."""

    @abstractmethod
    def embed(self, texts: list[str]) -> list[Any]: ...


class VectorStore(ABC):
    """Stage 3 — persists embeddings for later similarity search."""

    @abstractmethod
    def add(self, doc_id: str, vector: Any) -> None: ...

    @abstractmethod
    def search(self, query: Any, top_k: int) -> list[tuple[str, float]]: ...


class Retriever(ABC):
    """Stage 4 — finds candidate chunk ids relevant to a query."""

    @abstractmethod
    def retrieve(self, query: str, top_k: int) -> list[tuple[str, float]]: ...


class Reranker(ABC):
    """Stage 5 — reorders retrieved candidates by relevance."""

    @abstractmethod
    def rerank(
        self, query: str, candidates: list[tuple[str, float]]
    ) -> list[tuple[str, float]]: ...


class Generator(ABC):
    """Stage 6 — produces a final answer from a query and its context."""

    @abstractmethod
    def generate(self, query: str, context: list[str]) -> str: ...


class Evaluator(ABC):
    """Stage 7 — scores the quality of a generated answer."""

    @abstractmethod
    def evaluate(self, query: str, answer: str, context: list[str]) -> float: ...


class Observer(ABC):
    """Stage 8 — records pipeline events for monitoring."""

    @abstractmethod
    def record(self, event: str, **data: Any) -> None: ...
