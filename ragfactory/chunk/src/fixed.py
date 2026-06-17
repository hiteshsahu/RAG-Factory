from __future__ import annotations

from ragfactory.core import Chunk, Chunker, RawDocument


class FixedSizeChunker(Chunker):
    """Splits a document into overlapping fixed-size word windows (The Chunk-Inator)."""

    def __init__(self, chunk_size: int = 200, overlap: int = 50) -> None:
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        self._chunk_size = chunk_size
        self._overlap = overlap

    def chunk(self, document: RawDocument) -> list[Chunk]:
        words = document.content.split()
        if not words:
            return []

        step = self._chunk_size - self._overlap
        chunks = []
        for index, start in enumerate(range(0, len(words), step)):
            window = words[start : start + self._chunk_size]
            chunks.append(
                Chunk(
                    content=" ".join(window),
                    metadata=document.metadata,
                    chunk_id=f"{document.source_id}-{index}",
                    doc_id=document.source_id,
                )
            )
            if start + self._chunk_size >= len(words):
                break
        return chunks
