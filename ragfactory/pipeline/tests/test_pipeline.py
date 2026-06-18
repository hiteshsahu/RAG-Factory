from pathlib import Path

from ragfactory.chunk import FixedSizeChunker
from ragfactory.embed import HashingEmbedder
from ragfactory.evaluate import KeywordOverlapEvaluator
from ragfactory.generate import TemplateGenerator
from ragfactory.ingest import TextFileIngestor
from ragfactory.observe import LoggingObserver
from ragfactory.pipeline import Pipeline, PipelineConfig
from ragfactory.rerank import IdentityReranker
from ragfactory.retrieve import DenseRetriever, SparseRetriever
from ragfactory.store import InMemoryVectorStore


def build_pipeline(source_dir: Path) -> Pipeline:
    embedder = HashingEmbedder(dim=64)
    store = InMemoryVectorStore()
    return Pipeline(
        ingestor=TextFileIngestor(source_dir),
        chunker=FixedSizeChunker(chunk_size=20, overlap=5),
        embedder=embedder,
        store=store,
        retriever=DenseRetriever(embedder, store),
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


def test_sparse_retriever_corpus_is_populated_automatically_by_index(tmp_path: Path):
    """Pipeline.index() must call retriever.index(chunks) for retrievers that need
    their own corpus (e.g. BM25) -- not just dense retrievers backed by the store."""
    (tmp_path / "doc.txt").write_text("Doofenshmirtz builds the Raginator in his lab.")

    embedder = HashingEmbedder(dim=64)
    store = InMemoryVectorStore()
    sparse = SparseRetriever()
    pipeline = Pipeline(
        ingestor=TextFileIngestor(tmp_path),
        chunker=FixedSizeChunker(chunk_size=20, overlap=5),
        embedder=embedder,
        store=store,
        retriever=sparse,
        reranker=IdentityReranker(),
        generator=TemplateGenerator(),
        evaluator=KeywordOverlapEvaluator(),
        observer=LoggingObserver(),
    )

    pipeline.index()
    answer = pipeline.query("Raginator")

    assert "Raginator" in answer.answer
    assert answer.sources


def test_from_config_builds_a_working_default_pipeline(tmp_path: Path):
    (tmp_path / "doc.txt").write_text("Doofenshmirtz builds the Raginator in his lab.")
    config = PipelineConfig(
        source_dir=str(tmp_path), chunk_size=20, chunk_overlap=5, embedding_dim=32, top_k=3
    )

    pipeline = Pipeline.from_config(config)
    chunk_count = pipeline.index()
    assert chunk_count > 0

    answer = pipeline.query("Raginator")
    assert "Raginator" in answer.answer


def test_from_config_top_k_is_the_query_default(tmp_path: Path):
    (tmp_path / "doc.txt").write_text("a b c d e f g h i j")
    config = PipelineConfig(source_dir=str(tmp_path), chunk_size=2, chunk_overlap=0, top_k=1)

    pipeline = Pipeline.from_config(config)
    pipeline.index()

    answer = pipeline.query("a")
    assert len(answer.sources) <= 1
