"""Runs the toy RAG pipeline end to end against a single sample document."""

import tempfile
from pathlib import Path

from ragfactory.chunk import FixedSizeChunker
from ragfactory.embed import HashingEmbedder
from ragfactory.evaluate import KeywordOverlapEvaluator
from ragfactory.generate import TemplateGenerator
from ragfactory.ingest import TextFileIngestor
from ragfactory.observe import LoggingObserver
from ragfactory.pipeline import Pipeline
from ragfactory.rerank import IdentityReranker
from ragfactory.retrieve import DenseRetriever
from ragfactory.store import InMemoryVectorStore

SAMPLE_TEXT = "Behold the RAGINATOR! It RAG-ifies everything in the tri-state area."
QUESTION = "What does the RAGINATOR do?"


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        Path(tmp_dir, "doc.txt").write_text(SAMPLE_TEXT)

        embedder = HashingEmbedder(dim=64)
        store = InMemoryVectorStore()
        pipeline = Pipeline(
            ingestor=TextFileIngestor(tmp_dir),
            chunker=FixedSizeChunker(chunk_size=10, overlap=2),
            embedder=embedder,
            store=store,
            retriever=DenseRetriever(embedder, store),
            reranker=IdentityReranker(),
            generator=TemplateGenerator(),
            evaluator=KeywordOverlapEvaluator(),
            observer=LoggingObserver(),
        )

        print(f"indexed {pipeline.index()} chunks")
        answer = pipeline.query(QUESTION)
        print(answer.answer)
        print(f"\n({len(answer.sources)} source(s))")


if __name__ == "__main__":
    main()
