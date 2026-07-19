# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import Mock, patch

import pytest
from raginator.core import Chunk, GeneratedAnswer, RetrievedChunk, StageError
from raginator.evaluate import GenerationEvaluator, heuristic_generation_scores, llm_judge_scores


def _context(text: str) -> RetrievedChunk:
    chunk = Chunk(content=text, metadata={}, chunk_id="c", doc_id="d")
    return RetrievedChunk(chunk=chunk, score=1.0, rank=0)


def test_heuristic_scores_reward_grounded_relevant_answers():
    answer = GeneratedAnswer(answer="raginator dominates tri-state area", sources=[])
    context = [_context("the raginator dominates the tri-state area")]

    scores = heuristic_generation_scores("what does the raginator dominate", answer, context)

    assert scores.faithfulness > 0.5
    assert scores.relevance > 0.0


def test_heuristic_scores_zero_for_empty_answer():
    answer = GeneratedAnswer(answer="", sources=[])

    scores = heuristic_generation_scores("query", answer, [])

    assert scores.faithfulness == 0.0


def test_generation_evaluator_averages_subscores():
    answer = GeneratedAnswer(answer="raginator", sources=[])

    score = GenerationEvaluator().evaluate("raginator", answer, [])

    assert 0.0 <= score <= 1.0


def test_llm_judge_parses_json_response():
    response = Mock(status_code=200)
    response.raise_for_status = Mock()
    response.json.return_value = {
        "choices": [{"message": {"content": '{"faithfulness": 0.8, "relevance": 0.6}'}}]
    }

    with patch("raginator.evaluate.generation.requests.post", return_value=response):
        scores = llm_judge_scores(
            "q", GeneratedAnswer(answer="a", sources=[]), [], api_key="test-key"
        )

    assert scores.faithfulness == 0.8
    assert scores.relevance == 0.6


def test_llm_judge_missing_api_key_raises_stage_error(monkeypatch):
    monkeypatch.delenv("RAGINATOR_MISTRAL_API_KEY", raising=False)

    with pytest.raises(StageError):
        llm_judge_scores("q", GeneratedAnswer(answer="a", sources=[]), [])
