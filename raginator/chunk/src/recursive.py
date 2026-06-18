from __future__ import annotations

from raginator.core import Chunk, Chunker, RawDocument

DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


class RecursiveChunker(Chunker):
    """Splits text by trying separators in order -- paragraphs, then lines, then
    sentences, then words, then characters -- merging pieces back up to
    chunk_size with overlap (The Chunk-Inator, recursive mode).
    """

    def __init__(
        self,
        chunk_size: int = 200,
        overlap: int = 50,
        separators: list[str] | None = None,
    ) -> None:
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        self._chunk_size = chunk_size
        self._overlap = overlap
        self._separators = separators or DEFAULT_SEPARATORS

    def chunk(self, document: RawDocument) -> list[Chunk]:
        pieces = self._split(document.content, self._separators)
        merged = self._merge(pieces)
        return [
            Chunk(
                content=piece,
                metadata=document.metadata,
                chunk_id=f"{document.source_id}-{index}",
                doc_id=document.source_id,
            )
            for index, piece in enumerate(merged)
            if piece.strip()
        ]

    def _split(self, text: str, separators: list[str]) -> list[str]:
        if len(text) <= self._chunk_size or not separators:
            return [text]

        separator, *rest = separators
        parts = text.split(separator) if separator else list(text)

        pieces = []
        for part in parts:
            if len(part) > self._chunk_size:
                pieces.extend(self._split(part, rest))
            else:
                pieces.append(part)
        return pieces

    def _merge(self, pieces: list[str]) -> list[str]:
        merged: list[str] = []
        current = ""
        for piece in pieces:
            candidate = f"{current} {piece}".strip() if current else piece
            if len(candidate) <= self._chunk_size:
                current = candidate
            else:
                if current:
                    merged.append(current)
                current = piece
        if current:
            merged.append(current)

        if not self._overlap or len(merged) <= 1:
            return merged

        overlapped = [merged[0]]
        for previous, piece in zip(merged, merged[1:], strict=True):
            tail = previous[-self._overlap :]
            overlapped.append(f"{tail} {piece}".strip())
        return overlapped
