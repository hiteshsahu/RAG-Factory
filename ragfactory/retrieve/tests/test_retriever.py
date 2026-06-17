from ragfactory.core import Embedder, VectorStore
from ragfactory.retrieve import TopKRetriever


class FakeEmbedder(Embedder):
    def embed(self, texts):
        return [text.upper() for text in texts]


class FakeStore(VectorStore):
    def __init__(self):
        self.queries = []

    def add(self, doc_id, vector):
        raise NotImplementedError

    def search(self, query, top_k):
        self.queries.append((query, top_k))
        return [("doc-1", 0.9)]


def test_retrieve_embeds_query_then_searches_store():
    store = FakeStore()
    retriever = TopKRetriever(FakeEmbedder(), store)

    results = retriever.retrieve("hello", top_k=3)

    assert results == [("doc-1", 0.9)]
    assert store.queries == [("HELLO", 3)]
