from __future__ import annotations

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
    if name == "ChromaDB":
        return ChromaVectorStore(collection_name="raginator-bridge")
    if name == "pgvector":
        return PgVectorStore()
    raise ValueError(f"Unknown vector store: {name}")  # pragma: no cover -- Literal-exhaustive
