from __future__ import annotations

import json
from typing import Any

import psycopg
from ragfactory.core import Chunk, EmbeddedChunk, RetrievedChunk, Settings, StageError, VectorStore


class PgVectorStore(VectorStore):
    """Vector store backed by PostgreSQL + the pgvector extension (The Store-Inator, production)."""

    def __init__(
        self,
        dsn: str | None = None,
        table: str = "ragfactory_chunks",
        dimension: int = 256,
        connection: Any | None = None,
    ) -> None:
        self._table = table
        self._dimension = dimension

        if connection is not None:
            self._connection = connection
        else:
            resolved_dsn = dsn if dsn is not None else Settings().postgres_dsn
            if not resolved_dsn:
                raise StageError(
                    "store", "Postgres DSN not set (pass dsn= or set RAGFACTORY_POSTGRES_DSN)"
                )
            self._connection = psycopg.connect(resolved_dsn)
        self._ensure_table()

    def _ensure_table(self) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self._table} (
                    chunk_id TEXT PRIMARY KEY,
                    doc_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata JSONB NOT NULL,
                    embedding VECTOR({self._dimension})
                )
                """
            )
        self._connection.commit()

    def add(self, embedded_chunk: EmbeddedChunk) -> None:
        chunk = embedded_chunk.chunk
        with self._connection.cursor() as cursor:
            cursor.execute(
                f"""
                INSERT INTO {self._table} (chunk_id, doc_id, content, metadata, embedding)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (chunk_id) DO UPDATE SET
                    doc_id = EXCLUDED.doc_id,
                    content = EXCLUDED.content,
                    metadata = EXCLUDED.metadata,
                    embedding = EXCLUDED.embedding
                """,
                (
                    chunk.chunk_id,
                    chunk.doc_id,
                    chunk.content,
                    json.dumps(chunk.metadata),
                    embedded_chunk.embedding,
                ),
            )
        self._connection.commit()

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[RetrievedChunk]:
        with self._connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT chunk_id, doc_id, content, metadata, 1 - (embedding <=> %s) AS score
                FROM {self._table}
                ORDER BY embedding <=> %s
                LIMIT %s
                """,
                (query_embedding, query_embedding, top_k),
            )
            rows = cursor.fetchall()

        retrieved = []
        for rank, (chunk_id, doc_id, content, metadata, score) in enumerate(rows):
            if isinstance(metadata, str):
                metadata = json.loads(metadata)
            chunk = Chunk(content=content, metadata=metadata, chunk_id=chunk_id, doc_id=doc_id)
            retrieved.append(RetrievedChunk(chunk=chunk, score=float(score), rank=rank))
        return retrieved
