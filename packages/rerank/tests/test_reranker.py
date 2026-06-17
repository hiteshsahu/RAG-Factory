from ragfactory.rerank import IdentityReranker


def test_identity_reranker_preserves_order():
    candidates = [("a", 0.9), ("b", 0.5)]

    assert IdentityReranker().rerank("query", candidates) == candidates
