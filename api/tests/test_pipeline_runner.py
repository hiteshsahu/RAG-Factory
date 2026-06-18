from api.pipeline_runner import _suggest_questions
from raginator.core import Chunk, GeneratedAnswer, Generator, RetrievedChunk


class _StubGenerator(Generator):
    def __init__(self, answer_text: str) -> None:
        self._answer_text = answer_text
        self.last_context: list[RetrievedChunk] | None = None

    def generate(self, query: str, context: list[RetrievedChunk]) -> GeneratedAnswer:
        self.last_context = context
        return GeneratedAnswer(answer=self._answer_text, sources=context)


def _chunk(content: str, i: int) -> Chunk:
    return Chunk(content=content, metadata={}, chunk_id=f"c{i}", doc_id="doc")


def test_strips_numbering_and_bullets():
    generator = _StubGenerator("1. What is X?\n- How does Y work?\n* Why Z?")
    questions = _suggest_questions(generator, [_chunk("hello", 0)])
    assert questions == ["What is X?", "How does Y work?", "Why Z?"]


def test_drops_blank_lines_and_caps_at_three():
    generator = _StubGenerator("Q1?\n\nQ2?\nQ3?\nQ4?")
    questions = _suggest_questions(generator, [_chunk("hello", 0)])
    assert questions == ["Q1?", "Q2?", "Q3?"]


def test_samples_at_most_six_chunks_as_context():
    generator = _StubGenerator("Q?")
    chunks = [_chunk(f"chunk {i}", i) for i in range(10)]
    _suggest_questions(generator, chunks)
    assert generator.last_context is not None
    assert len(generator.last_context) == 6
