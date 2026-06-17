from ragfactory.core import Chunk
from ragfactory.retrieve import SparseRetriever


def _chunk(chunk_id: str, content: str) -> Chunk:
    return Chunk(content=content, metadata={}, chunk_id=chunk_id, doc_id="doc")


def test_ranks_by_keyword_overlap():
    retriever = SparseRetriever()
    retriever.index(
        [
            _chunk("cats", "Cats are great pets and cats nap a lot"),
            _chunk("dogs", "Dogs are loyal and dogs love to fetch balls"),
            _chunk("unrelated", "The weather today is sunny and warm"),
        ]
    )

    results = retriever.retrieve("cats nap", top_k=2)

    assert results[0].chunk.chunk_id == "cats"
    assert results[0].rank == 0
    assert len(results) == 2
    assert all(r.score >= 0 for r in results)


def test_empty_corpus_returns_nothing():
    assert SparseRetriever().retrieve("anything") == []


def test_index_accumulates_across_calls():
    retriever = SparseRetriever()
    retriever.index([_chunk("a", "alpha")])
    retriever.index([_chunk("b", "beta")])

    results = retriever.retrieve("beta", top_k=2)

    assert {r.chunk.chunk_id for r in results} == {"a", "b"}
    assert results[0].chunk.chunk_id == "b"
