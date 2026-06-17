from ragfactory.chunk import RecursiveChunker
from ragfactory.core import RawDocument


def _doc(text: str) -> RawDocument:
    return RawDocument(content=text, metadata={}, source_id="doc")


def test_splits_on_paragraphs_first():
    text = "First paragraph here.\n\nSecond paragraph here.\n\nThird paragraph here."
    chunker = RecursiveChunker(chunk_size=30, overlap=0)

    chunks = chunker.chunk(_doc(text))

    assert len(chunks) >= 2
    assert all(len(c.content) <= 30 for c in chunks)
    assert chunks[0].doc_id == "doc"
    assert chunks[0].chunk_id == "doc-0"


def test_merges_small_pieces_up_to_chunk_size():
    text = "a.\n\nb.\n\nc.\n\nd."
    chunker = RecursiveChunker(chunk_size=10, overlap=0)

    chunks = chunker.chunk(_doc(text))

    assert [c.content for c in chunks] == ["a. b. c.", "d."]


def test_empty_text_yields_no_chunks():
    assert RecursiveChunker().chunk(_doc("")) == []


def test_overlap_must_be_smaller_than_chunk_size():
    try:
        RecursiveChunker(chunk_size=4, overlap=4)
    except ValueError:
        return
    raise AssertionError("expected ValueError")
