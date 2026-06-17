import numpy as np
from ragfactory.core import Chunk
from ragfactory.embed import HashingEmbedder


def test_embed_is_deterministic_and_normalized():
    embedder = HashingEmbedder(dim=32)

    [vector] = embedder.embed_texts(["raginator tri-state area"])

    assert len(vector) == 32
    assert np.isclose(np.linalg.norm(vector), 1.0)
    [vector_again] = embedder.embed_texts(["raginator tri-state area"])
    assert vector == vector_again


def test_embed_empty_text_returns_zero_vector():
    [vector] = HashingEmbedder(dim=16).embed_texts([""])
    assert all(v == 0 for v in vector)


def test_embed_chunks_wraps_into_embedded_chunk():
    embedder = HashingEmbedder(dim=8)
    chunk = Chunk(content="hello world", metadata={}, chunk_id="c1", doc_id="d1")

    [embedded] = embedder.embed_chunks([chunk])

    assert embedded.chunk is chunk
    assert embedded.provider == "hashing"
    assert len(embedded.embedding) == 8
