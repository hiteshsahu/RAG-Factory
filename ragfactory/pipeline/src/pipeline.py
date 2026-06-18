from __future__ import annotations

from typing import Self

from ragfactory.core import (
    Chunker,
    Embedder,
    Evaluator,
    GeneratedAnswer,
    Generator,
    Ingestor,
    Observer,
    Reranker,
    Retriever,
    VectorStore,
)

from .config import PipelineConfig


class Pipeline:
    """Wires the nine RAG stages together: ingest -> chunk -> embed -> store
    -> retrieve -> rerank -> generate -> evaluate -> observe."""

    def __init__(
        self,
        ingestor: Ingestor,
        chunker: Chunker,
        embedder: Embedder,
        store: VectorStore,
        retriever: Retriever,
        reranker: Reranker,
        generator: Generator,
        evaluator: Evaluator,
        observer: Observer,
        default_top_k: int = 5,
    ) -> None:
        self._ingestor = ingestor
        self._chunker = chunker
        self._embedder = embedder
        self._store = store
        self._retriever = retriever
        self._reranker = reranker
        self._generator = generator
        self._evaluator = evaluator
        self._observer = observer
        self._default_top_k = default_top_k

    @classmethod
    def from_config(cls, config: PipelineConfig | None = None) -> Self:
        """Builds the dependency-free default pipeline (toy implementations
        only), tuned by PipelineConfig. Construct a Pipeline directly instead
        to wire in real providers (Mistral, Chroma, pgvector, ...) -- the
        concrete classes are imported here, lazily, so just importing
        ragfactory.pipeline doesn't pull in every other stage's deps.
        """
        from ragfactory.chunk import FixedSizeChunker
        from ragfactory.embed import HashingEmbedder
        from ragfactory.evaluate import KeywordOverlapEvaluator
        from ragfactory.generate import TemplateGenerator
        from ragfactory.ingest import TextFileIngestor
        from ragfactory.observe import LoggingObserver
        from ragfactory.rerank import IdentityReranker
        from ragfactory.retrieve import DenseRetriever
        from ragfactory.store import InMemoryVectorStore

        config = config or PipelineConfig()
        embedder = HashingEmbedder(dim=config.embedding_dim)
        store = InMemoryVectorStore()
        return cls(
            ingestor=TextFileIngestor(config.source_dir),
            chunker=FixedSizeChunker(
                chunk_size=config.chunk_size, overlap=config.chunk_overlap
            ),
            embedder=embedder,
            store=store,
            retriever=DenseRetriever(embedder, store),
            reranker=IdentityReranker(),
            generator=TemplateGenerator(),
            evaluator=KeywordOverlapEvaluator(),
            observer=LoggingObserver(),
            default_top_k=config.top_k,
        )

    def index(self) -> int:
        """Ingest, chunk, embed, and store all documents. Returns the chunk count."""
        count = 0
        for document in self._ingestor.ingest():
            chunks = self._chunker.chunk(document)
            self._retriever.index(chunks)
            for embedded_chunk in self._embedder.embed_chunks(chunks):
                self._store.add(embedded_chunk)
                count += 1
        self._observer.record("indexed", chunk_count=count)
        return count

    def query(self, question: str, top_k: int | None = None) -> GeneratedAnswer:
        """Retrieve, rerank, generate, and evaluate an answer for a question."""
        candidates = self._retriever.retrieve(
            question, top_k=top_k if top_k is not None else self._default_top_k
        )
        reranked = self._reranker.rerank(question, candidates)
        answer = self._generator.generate(question, reranked)
        score = self._evaluator.evaluate(question, answer, reranked)
        self._observer.record("query", question=question, score=score)
        return answer
