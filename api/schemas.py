# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

Provider = Literal["Mistral", "OpenAI", "Ollama"]
VectorStoreName = Literal["ChromaDB", "pgvector"]
ChunkStrategy = Literal["Fixed", "Recursive", "Semantic", "Code"]

# Mirrors frontend/src/data/index.ts's EMBED_MODELS/LLM_MODELS exactly -- these
# are the real default model ids from raginator's actual provider classes.
EMBED_MODELS: dict[Provider, str] = {
    "Mistral": "mistral-embed",
    "OpenAI": "text-embedding-3-small",
    "Ollama": "nomic-embed-text",
}
LLM_MODELS: dict[Provider, str] = {
    "Mistral": "mistral-small-latest",
    "OpenAI": "gpt-4o-mini",
    "Ollama": "llama3.2",
}


class CamelModel(BaseModel):
    """Base for every request/response model -- JSON in/out is camelCase to
    match the frontend's TypeScript types directly, Python stays snake_case."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class PipelineSettings(CamelModel):
    # Ollama -- mirrors frontend/src/data/index.ts's DEFAULT_SETTINGS exactly,
    # since it needs no API key to work out of the box.
    embed_provider: Provider = "Ollama"
    vector_store: VectorStoreName = "ChromaDB"
    llm_provider: Provider = "Ollama"
    chunk_strategy: ChunkStrategy = "Semantic"


class SourceChunk(CamelModel):
    path: str
    text: str
    score: float


class QueryRequest(CamelModel):
    query: str


class QueryResponse(CamelModel):
    answer: str
    sources: list[SourceChunk]
    ms: float
    tokens: int
    cost: str


class CorpusStats(CamelModel):
    docs: int
    chunks: int
    avg_chunk_tokens: int
    embedding_model: str
    index_size_bytes: int
