# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import Mock, patch

import pytest
from api.pipeline_runner import (
    _github_owner_repo,
    _ingest_pasted_text,
    _ingest_urls,
    _suggest_questions,
)
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


def test_github_owner_repo_parses_path():
    assert _github_owner_repo("https://github.com/HiteshSahu/RAG-Factory") == ("HiteshSahu", "RAG-Factory")


def test_github_owner_repo_rejects_bare_url():
    with pytest.raises(ValueError, match="owner/repo"):
        _github_owner_repo("https://github.com/HiteshSahu")


def test_ingest_urls_dispatches_by_hostname():
    web_response = Mock(text="<p>Hello Web</p>", status_code=200)
    web_response.raise_for_status = Mock()

    github_tree = Mock(status_code=200)
    github_tree.raise_for_status = Mock()
    github_tree.json.return_value = {
        "tree": [{"path": "README.md", "type": "blob", "url": "https://api.github.com/blob/1"}]
    }
    github_blob = Mock(status_code=200)
    github_blob.raise_for_status = Mock()
    github_blob.json.return_value = {"content": "SGVsbG8gUkVBRE1F"}  # base64 "Hello README"

    # web.py and github.py both `import requests` -- the same module object --
    # so patching each module's `.requests.get` attribute separately clobbers
    # whichever was patched first. One patch on the shared `requests.get`,
    # ordered to match the call sequence (web fetch, then repo tree, then blob).
    with patch("requests.get", side_effect=[web_response, github_tree, github_blob]):
        documents = _ingest_urls(["https://example.com", "https://github.com/owner/repo"])

    assert {d.source_id for d in documents} == {"https://example.com", "owner/repo/README.md"}


def test_ingest_pasted_text_assigns_stable_source_ids():
    documents = _ingest_pasted_text(["Hello RAGINATOR", "Second blob"])

    assert [d.content for d in documents] == ["Hello RAGINATOR", "Second blob"]
    assert [d.source_id for d in documents] == ["pasted-1", "pasted-2"]
    assert all(d.metadata["source"] == "pasted" for d in documents)
