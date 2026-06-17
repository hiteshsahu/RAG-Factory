import chromadb
from ragfactory.core import Chunk, EmbeddedChunk
from ragfactory.store import ChromaVectorStore


def _embedded(chunk_id: str, vector: list[float]) -> EmbeddedChunk:
    chunk = Chunk(content=f"content for {chunk_id}", metadata={"source": "test"}, chunk_id=chunk_id, doc_id="doc")
    return EmbeddedChunk(chunk=chunk, embedding=vector, provider="test")


def test_chroma_store_add_and_search_roundtrip():
    store = ChromaVectorStore(collection_name="test", client=chromadb.Client())
    store.add(_embedded("same", [1.0, 0.0, 0.0]))
    store.add(_embedded("orthogonal", [0.0, 1.0, 0.0]))

    [result] = store.search([1.0, 0.0, 0.0], top_k=1)

    assert result.chunk.chunk_id == "same"
    assert result.chunk.content == "content for same"
    assert result.chunk.doc_id == "doc"
    assert result.chunk.metadata == {"source": "test"}
    assert result.rank == 0
