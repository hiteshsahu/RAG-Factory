from ragfactory.chunk import FixedSizeChunker


def test_chunks_with_overlap():
    chunker = FixedSizeChunker(chunk_size=4, overlap=2)
    text = "a b c d e f g h"

    chunks = chunker.chunk(text)

    assert chunks[0] == "a b c d"
    assert chunks[1] == "c d e f"
    assert chunks[-1].endswith("h")


def test_empty_text_yields_no_chunks():
    assert FixedSizeChunker().chunk("") == []


def test_overlap_must_be_smaller_than_chunk_size():
    try:
        FixedSizeChunker(chunk_size=4, overlap=4)
    except ValueError:
        return
    raise AssertionError("expected ValueError")
