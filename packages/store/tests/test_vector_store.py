import numpy as np

from ragfactory.store import InMemoryVectorStore


def test_search_ranks_by_cosine_similarity():
    store = InMemoryVectorStore()
    store.add("same", np.array([1.0, 0.0]))
    store.add("opposite", np.array([-1.0, 0.0]))
    store.add("orthogonal", np.array([0.0, 1.0]))

    results = store.search(np.array([1.0, 0.0]), top_k=3)

    assert results[0][0] == "same"
    assert results[-1][0] == "opposite"


def test_search_on_empty_store_returns_nothing():
    assert InMemoryVectorStore().search(np.array([1.0, 0.0])) == []
