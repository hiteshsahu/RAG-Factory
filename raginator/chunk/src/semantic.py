from __future__ import annotations

import math
import re

from raginator.core import Chunk, Chunker, Embedder, RawDocument

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


class SemanticChunker(Chunker):
    """Groups sentences into chunks, starting a new chunk wherever consecutive
    sentences diverge semantically (The Chunk-Inator, semantic mode).

    Requires an Embedder to score sentence-to-sentence similarity; swap in any
    real embedding model for production use.
    """

    def __init__(self, embedder: Embedder, breakpoint_threshold: float = 0.5) -> None:
        self._embedder = embedder
        self._breakpoint_threshold = breakpoint_threshold

    def chunk(self, document: RawDocument) -> list[Chunk]:
        sentences = [s for s in _SENTENCE_SPLIT_RE.split(document.content.strip()) if s]
        if not sentences:
            return []

        groups = self._group_by_similarity(sentences)
        return [
            Chunk(
                content=" ".join(group),
                metadata=document.metadata,
                chunk_id=f"{document.source_id}-{index}",
                doc_id=document.source_id,
            )
            for index, group in enumerate(groups)
        ]

    def _group_by_similarity(self, sentences: list[str]) -> list[list[str]]:
        if len(sentences) == 1:
            return [sentences]

        embeddings = self._embedder.embed_texts(sentences)
        groups: list[list[str]] = [[sentences[0]]]
        for sentence, previous_embedding, embedding in zip(
            sentences[1:], embeddings[:-1], embeddings[1:], strict=True
        ):
            similarity = _cosine_similarity(previous_embedding, embedding)
            if similarity < self._breakpoint_threshold:
                groups.append([])
            groups[-1].append(sentence)
        return groups


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
