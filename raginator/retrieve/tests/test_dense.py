from raginator.core import Chunk, Embedder, RetrievedChunk, VectorStore
from raginator.retrieve import DenseRetriever


class FakeEmbedder(Embedder):
    def embed_texts(self, texts):
        return [[float(len(text))] for text in texts]


class FakeStore(VectorStore):
    def __init__(self):
        self.queries = []

    def add(self, embedded_chunk):
        raise NotImplementedError

    def search(self, query_embedding, top_k):
        self.queries.append((query_embedding, top_k))
        chunk = Chunk(content="x", metadata={}, chunk_id="doc-1", doc_id="doc")
        return [RetrievedChunk(chunk=chunk, score=0.9, rank=0)]


def test_retrieve_embeds_query_then_searches_store():
    store = FakeStore()
    retriever = DenseRetriever(FakeEmbedder(), store)

    results = retriever.retrieve("hello", top_k=3)

    assert results[0].chunk.chunk_id == "doc-1"
    assert results[0].score == 0.9
    assert store.queries == [([5.0], 3)]
