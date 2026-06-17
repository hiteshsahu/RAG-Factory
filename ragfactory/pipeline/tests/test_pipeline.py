from pathlib import Path

from ragfactory.chunk import FixedSizeChunker
from ragfactory.embed import HashingEmbedder
from ragfactory.evaluate import KeywordOverlapEvaluator
from ragfactory.generate import TemplateGenerator
from ragfactory.ingest import TextFileIngestor
from ragfactory.observe import LoggingObserver
from ragfactory.pipeline import Pipeline
from ragfactory.rerank import IdentityReranker
from ragfactory.retrieve import TopKRetriever
from ragfactory.store import InMemoryVectorStore


def build_pipeline(source_dir: Path) -> Pipeline:
    embedder = HashingEmbedder(dim=64)
    store = InMemoryVectorStore()
    return Pipeline(
        ingestor=TextFileIngestor(source_dir),
        chunker=FixedSizeChunker(chunk_size=20, overlap=5),
        embedder=embedder,
        store=store,
        retriever=TopKRetriever(embedder, store),
        reranker=IdentityReranker(),
        generator=TemplateGenerator(),
        evaluator=KeywordOverlapEvaluator(),
        observer=LoggingObserver(),
    )


def test_end_to_end_index_and_query(tmp_path: Path):
    (tmp_path / "doc.txt").write_text(
        "Doofenshmirtz builds the Raginator to dominate the Tri-State Area."
    )

    pipeline = build_pipeline(tmp_path)
    chunk_count = pipeline.index()
    assert chunk_count > 0

    answer = pipeline.query("What does the Raginator do?")
    assert "Raginator" in answer.answer
    assert answer.sources
