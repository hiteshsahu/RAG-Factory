from raginator.core import Chunk, RetrievedChunk
from raginator.generate import TemplateGenerator


def _context(text: str) -> RetrievedChunk:
    chunk = Chunk(content=text, metadata={}, chunk_id="c", doc_id="d")
    return RetrievedChunk(chunk=chunk, score=1.0, rank=0)


def test_generate_includes_context():
    answer = TemplateGenerator().generate(
        "What is RAG?", [_context("chunk one"), _context("chunk two")]
    )

    assert "What is RAG?" in answer.answer
    assert "chunk one" in answer.answer
    assert "chunk two" in answer.answer
    assert len(answer.sources) == 2


def test_generate_without_context():
    answer = TemplateGenerator().generate("unanswerable", [])

    assert "No context found" in answer.answer
    assert answer.sources == []
