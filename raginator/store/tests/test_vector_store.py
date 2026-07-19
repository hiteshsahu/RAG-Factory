# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from raginator.core import Chunk, EmbeddedChunk
from raginator.store import InMemoryVectorStore


def _embedded(chunk_id: str, vector: list[float]) -> EmbeddedChunk:
    chunk = Chunk(content=chunk_id, metadata={}, chunk_id=chunk_id, doc_id="doc")
    return EmbeddedChunk(chunk=chunk, embedding=vector, provider="test")


def test_search_ranks_by_cosine_similarity():
    store = InMemoryVectorStore()
    store.add(_embedded("same", [1.0, 0.0]))
    store.add(_embedded("opposite", [-1.0, 0.0]))
    store.add(_embedded("orthogonal", [0.0, 1.0]))

    results = store.search([1.0, 0.0], top_k=3)

    assert results[0].chunk.chunk_id == "same"
    assert results[0].rank == 0
    assert results[-1].chunk.chunk_id == "opposite"


def test_search_on_empty_store_returns_nothing():
    assert InMemoryVectorStore().search([1.0, 0.0]) == []
