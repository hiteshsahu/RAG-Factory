# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from raginator.chunk import SemanticChunker
from raginator.core import Embedder, RawDocument


class FakeEmbedder(Embedder):
    """Embeds sentences into two obviously distinct clusters based on a keyword."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0] if "cat" in text.lower() else [0.0, 1.0] for text in texts]


def _doc(text: str) -> RawDocument:
    return RawDocument(content=text, metadata={}, source_id="doc")


def test_splits_where_topic_changes():
    text = "Cats are great. Cats nap a lot. Dogs are loyal. Dogs fetch balls."
    chunker = SemanticChunker(FakeEmbedder(), breakpoint_threshold=0.5)

    chunks = chunker.chunk(_doc(text))

    assert len(chunks) == 2
    assert "Cats" in chunks[0].content
    assert "Dogs" in chunks[1].content
    assert chunks[0].chunk_id == "doc-0"


def test_single_sentence_yields_one_chunk():
    chunker = SemanticChunker(FakeEmbedder())

    chunks = chunker.chunk(_doc("Only one sentence."))

    assert len(chunks) == 1
    assert chunks[0].content == "Only one sentence."


def test_empty_text_yields_no_chunks():
    assert SemanticChunker(FakeEmbedder()).chunk(_doc("")) == []
