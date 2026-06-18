from __future__ import annotations

import uuid

from api.schemas import ChunkStrategy, Provider, VectorStoreName
from raginator.chunk import CodeChunker, FixedSizeChunker, RecursiveChunker, SemanticChunker
from raginator.core import Chunker, Embedder, Generator, VectorStore
from raginator.embed import MistralEmbedder, OllamaEmbedder, OpenAIEmbedder
from raginator.generate import MistralGenerator, OllamaGenerator, OpenAIGenerator
from raginator.store import ChromaVectorStore, PgVectorStore

_EMBEDDERS = {
    "Mistral": MistralEmbedder,
    "OpenAI": OpenAIEmbedder,
    "Ollama": OllamaEmbedder,
}
_GENERATORS = {
    "Mistral": MistralGenerator,
    "OpenAI": OpenAIGenerator,
    "Ollama": OllamaGenerator,
}


def build_embedder(provider: Provider) -> Embedder:
    return _EMBEDDERS[provider]()


def build_generator(provider: Provider) -> Generator:
    return _GENERATORS[provider]()


def build_chunker(strategy: ChunkStrategy, embedder: Embedder) -> Chunker:
    if strategy == "Fixed":
        return FixedSizeChunker()
    if strategy == "Recursive":
        return RecursiveChunker()
    if strategy == "Semantic":
        return SemanticChunker(embedder=embedder)
    if strategy == "Code":
        return CodeChunker()
    raise ValueError(f"Unknown chunk strategy: {strategy}")  # pragma: no cover -- Literal-exhaustive


def build_store(name: VectorStoreName) -> VectorStore:
    # The bridge is single-corpus-at-a-time by design (see api/main.py's
    # _STATE comment), but a fixed collection/table name would silently
    # accumulate every corpus ever indexed in this process: ChromaDB's
    # client shares state across instances with identical settings, and
    # pgvector's table just keeps existing rows around (INSERT, not
    # replace). A new chat would then retrieve chunks left over from
    # whatever was uploaded earlier in the same process -- give every run
    # its own isolated collection/table instead.
    run_id = uuid.uuid4().hex[:12]
    if name == "ChromaDB":
        return ChromaVectorStore(collection_name=f"raginator-bridge-{run_id}")
    if name == "pgvector":
        return PgVectorStore(table=f"raginator_chunks_{run_id}")
    raise ValueError(f"Unknown vector store: {name}")  # pragma: no cover -- Literal-exhaustive
