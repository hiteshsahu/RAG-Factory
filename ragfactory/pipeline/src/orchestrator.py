from __future__ import annotations

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

    def index(self) -> int:
        """Ingest, chunk, embed, and store all documents. Returns the chunk count."""
        count = 0
        for document in self._ingestor.ingest():
            chunks = self._chunker.chunk(document)
            for embedded_chunk in self._embedder.embed_chunks(chunks):
                self._store.add(embedded_chunk)
                count += 1
        self._observer.record("indexed", chunk_count=count)
        return count

    def query(self, question: str, top_k: int = 5) -> GeneratedAnswer:
        """Retrieve, rerank, generate, and evaluate an answer for a question."""
        candidates = self._retriever.retrieve(question, top_k=top_k)
        reranked = self._reranker.rerank(question, candidates)
        answer = self._generator.generate(question, reranked)
        score = self._evaluator.evaluate(question, answer, reranked)
        self._observer.record("query", question=question, score=score)
        return answer
