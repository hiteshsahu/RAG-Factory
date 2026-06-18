from raginator.core import Chunk, Embedder, RetrievedChunk, VectorStore
from raginator.retrieve import DenseRetriever, HybridRetriever, SparseRetriever


def _chunk(chunk_id: str, content: str) -> Chunk:
    return Chunk(content=content, metadata={}, chunk_id=chunk_id, doc_id="doc")


class FakeEmbedder(Embedder):
    """Embeds by keyword presence so dense results are deterministic in tests."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0] if "alpha" in text else [0.0, 1.0] for text in texts]


class FakeStore(VectorStore):
    def __init__(self) -> None:
        self._chunks: list[Chunk] = []
        self._vectors: list[list[float]] = []

    def add(self, embedded_chunk):
        self._chunks.append(embedded_chunk.chunk)
        self._vectors.append(embedded_chunk.embedding)

    def search(self, query_embedding, top_k):
        scored = [
            (chunk, sum(a * b for a, b in zip(query_embedding, vector, strict=True)))
            for chunk, vector in zip(self._chunks, self._vectors, strict=True)
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [
            RetrievedChunk(chunk=chunk, score=score, rank=rank)
            for rank, (chunk, score) in enumerate(scored[:top_k])
        ]


def test_hybrid_combines_dense_and_sparse_scores():
    embedder = FakeEmbedder()
    store = FakeStore()
    dense = DenseRetriever(embedder, store)
    sparse = SparseRetriever()
    hybrid = HybridRetriever(dense, sparse, alpha=0.5)

    chunks = [_chunk("alpha-doc", "alpha alpha alpha"), _chunk("beta-doc", "beta beta beta")]
    hybrid.index(chunks)
    for embedded_chunk in embedder.embed_chunks(chunks):
        store.add(embedded_chunk)

    results = hybrid.retrieve("alpha", top_k=2)

    assert results[0].chunk.chunk_id == "alpha-doc"
    assert len(results) == 2
