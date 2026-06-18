from raginator.chunk import FixedSizeChunker
from raginator.core import RawDocument


def _doc(text: str) -> RawDocument:
    return RawDocument(content=text, metadata={}, source_id="doc")


def test_chunks_with_overlap():
    chunker = FixedSizeChunker(chunk_size=4, overlap=2)

    chunks = chunker.chunk(_doc("a b c d e f g h"))

    assert chunks[0].content == "a b c d"
    assert chunks[1].content == "c d e f"
    assert chunks[-1].content.endswith("h")
    assert chunks[0].doc_id == "doc"
    assert chunks[0].chunk_id == "doc-0"


def test_empty_text_yields_no_chunks():
    assert FixedSizeChunker().chunk(_doc("")) == []


def test_overlap_must_be_smaller_than_chunk_size():
    try:
        FixedSizeChunker(chunk_size=4, overlap=4)
    except ValueError:
        return
    raise AssertionError("expected ValueError")
