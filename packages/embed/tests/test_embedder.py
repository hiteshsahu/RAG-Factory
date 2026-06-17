import numpy as np

from ragfactory.embed import HashingEmbedder


def test_embed_is_deterministic_and_normalized():
    embedder = HashingEmbedder(dim=32)

    [vector] = embedder.embed(["raginator tri-state area"])

    assert vector.shape == (32,)
    assert np.isclose(np.linalg.norm(vector), 1.0)
    [vector_again] = embedder.embed(["raginator tri-state area"])
    assert np.array_equal(vector, vector_again)


def test_embed_empty_text_returns_zero_vector():
    [vector] = HashingEmbedder(dim=16).embed([""])
    assert np.all(vector == 0)
