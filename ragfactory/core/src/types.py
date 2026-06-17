from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RawDocument:
    """Output of Stage 0 (ingest) — one raw document, before chunking."""

    content: str
    metadata: dict[str, Any]
    source_id: str


@dataclass
class Chunk:
    """Output of Stage 1 (chunk) — one retrievable slice of a document."""

    content: str
    metadata: dict[str, Any]
    chunk_id: str
    doc_id: str


@dataclass
class EmbeddedChunk:
    """Output of Stage 2 (embed) — a chunk paired with its vector embedding."""

    chunk: Chunk
    embedding: list[float]
    provider: str


@dataclass
class RetrievedChunk:
    """Output of Stage 4 (retrieve) / Stage 5 (rerank) — a scored, ranked chunk."""

    chunk: Chunk
    score: float
    rank: int


@dataclass
class GeneratedAnswer:
    """Output of Stage 6 (generate) — the final answer plus its provenance."""

    answer: str
    sources: list[RetrievedChunk]
    tokens_used: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0
