from typing import Any

import pytest
from raginator.core import Chunk, EmbeddedChunk, StageError
from raginator.store import PineconeVectorStore


class FakeIndex:
    def __init__(self) -> None:
        self.upserted: list[dict[str, Any]] = []

    def upsert(self, vectors: list[dict[str, Any]]) -> None:
        self.upserted.extend(vectors)

    def query(self, vector: list[float], top_k: int, include_metadata: bool) -> dict[str, Any]:
        return {
            "matches": [
                {"id": v["id"], "score": 0.9, "metadata": v["metadata"]}
                for v in self.upserted[:top_k]
            ]
        }


def test_pinecone_store_add_and_search_roundtrip():
    index = FakeIndex()
    store = PineconeVectorStore(index_name="test", index=index)
    chunk = Chunk(content="hello pinecone", metadata={"k": "v"}, chunk_id="c1", doc_id="doc")

    store.add(EmbeddedChunk(chunk=chunk, embedding=[0.1, 0.2], provider="test"))
    [result] = store.search([0.1, 0.2], top_k=1)

    assert result.chunk.chunk_id == "c1"
    assert result.chunk.content == "hello pinecone"
    assert result.chunk.metadata == {"k": "v"}
    assert result.score == 0.9


def test_missing_api_key_raises_stage_error(monkeypatch):
    monkeypatch.delenv("RAGINATOR_PINECONE_API_KEY", raising=False)

    with pytest.raises(StageError):
        PineconeVectorStore(index_name="test")
