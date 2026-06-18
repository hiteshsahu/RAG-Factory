from raginator.core import Chunk, EmbeddedChunk, GeneratedAnswer, RawDocument, RetrievedChunk


def test_data_flow_types_compose():
    document = RawDocument(content="hello world", metadata={"source": "test"}, source_id="doc-1")
    chunk = Chunk(content=document.content, metadata=document.metadata, chunk_id="doc-1-0", doc_id=document.source_id)
    embedded = EmbeddedChunk(chunk=chunk, embedding=[0.1, 0.2], provider="test")
    retrieved = RetrievedChunk(chunk=embedded.chunk, score=0.9, rank=0)
    answer = GeneratedAnswer(answer="hi", sources=[retrieved])

    assert answer.sources[0].chunk.doc_id == "doc-1"
    assert answer.tokens_used == 0
    assert answer.cost_usd == 0.0
