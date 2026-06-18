from __future__ import annotations

import json
import math
from typing import Any

from raginator.core import Chunk, EmbeddedChunk
from raginator.store import PgVectorStore


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return 0.0 if norm_a == 0 or norm_b == 0 else dot / (norm_a * norm_b)


class FakeCursor:
    """Stands in for a psycopg cursor, just enough to drive PgVectorStore in tests."""

    def __init__(self, connection: FakeConnection) -> None:
        self._connection = connection
        self._last_result: list[tuple[Any, ...]] = []

    def __enter__(self) -> FakeCursor:
        return self

    def __exit__(self, *exc: object) -> None:
        return None

    def execute(self, sql: str, params: tuple[Any, ...] | None = None) -> None:
        sql_upper = sql.strip().upper()
        if sql_upper.startswith("CREATE"):
            return
        if sql_upper.startswith("INSERT"):
            chunk_id, doc_id, content, metadata_json, embedding = params  # type: ignore[misc]
            self._connection.rows[chunk_id] = (chunk_id, doc_id, content, metadata_json, embedding)
            return
        if sql_upper.startswith("SELECT"):
            query_embedding, _, top_k = params  # type: ignore[misc]
            scored = [
                (chunk_id, doc_id, content, json.loads(metadata_json), _cosine_similarity(query_embedding, embedding))
                for chunk_id, doc_id, content, metadata_json, embedding in self._connection.rows.values()
            ]
            scored.sort(key=lambda row: row[-1], reverse=True)
            self._last_result = scored[:top_k]
            return
        raise AssertionError(f"unexpected SQL in test: {sql}")

    def fetchall(self) -> list[tuple[Any, ...]]:
        return self._last_result


class FakeConnection:
    def __init__(self) -> None:
        self.rows: dict[str, tuple[Any, ...]] = {}

    def cursor(self) -> FakeCursor:
        return FakeCursor(self)

    def commit(self) -> None:
        pass


def test_pgvector_store_add_and_search_roundtrip():
    store = PgVectorStore(connection=FakeConnection(), dimension=2)
    chunk = Chunk(content="same", metadata={"k": "v"}, chunk_id="same", doc_id="doc")
    store.add(EmbeddedChunk(chunk=chunk, embedding=[1.0, 0.0], provider="test"))

    [result] = store.search([1.0, 0.0], top_k=1)

    assert result.chunk.chunk_id == "same"
    assert result.chunk.content == "same"
    assert result.chunk.metadata == {"k": "v"}
    assert result.rank == 0
