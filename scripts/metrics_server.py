"""Runs the toy pipeline on a loop, exposing live metrics on :8000/metrics
for Prometheus to scrape -- see docker-compose.yml and `./go observe`."""

import tempfile
import time
from pathlib import Path

from prometheus_client import start_http_server
from raginator.chunk import FixedSizeChunker
from raginator.embed import HashingEmbedder
from raginator.evaluate import KeywordOverlapEvaluator
from raginator.generate import TemplateGenerator
from raginator.ingest import TextFileIngestor
from raginator.observe import PrometheusObserver
from raginator.pipeline import Pipeline
from raginator.rerank import IdentityReranker
from raginator.retrieve import DenseRetriever
from raginator.store import InMemoryVectorStore

PORT = 8000
SAMPLE_DOCS = {
    "doofenshmirtz.txt": "Behold the RAGINATOR! It RAG-ifies everything in the tri-state area.",
    "perry.txt": "Agent P infiltrates the lab to stop the Raginator before it activates.",
}
QUESTIONS = ["What does the RAGINATOR do?", "Who stops the Raginator?"]


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        for name, text in SAMPLE_DOCS.items():
            Path(tmp_dir, name).write_text(text)

        observer = PrometheusObserver()
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
            observer=observer,
        )

        start_http_server(PORT, registry=observer.registry)
        print(f"serving metrics on :{PORT}/metrics (Ctrl-C to stop)")

        pipeline.index()
        while True:
            for question in QUESTIONS:
                pipeline.query(question)
            time.sleep(5)


if __name__ == "__main__":
    main()
