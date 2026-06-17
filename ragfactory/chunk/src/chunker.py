from __future__ import annotations

from ragfactory.core import Chunker


class FixedSizeChunker(Chunker):
    """Splits text into overlapping fixed-size word windows (The Chunk-Inator)."""

    def __init__(self, chunk_size: int = 200, overlap: int = 50) -> None:
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        self._chunk_size = chunk_size
        self._overlap = overlap

    def chunk(self, text: str) -> list[str]:
        words = text.split()
        if not words:
            return []

        step = self._chunk_size - self._overlap
        chunks = []
        for start in range(0, len(words), step):
            window = words[start : start + self._chunk_size]
            chunks.append(" ".join(window))
            if start + self._chunk_size >= len(words):
                break
        return chunks
