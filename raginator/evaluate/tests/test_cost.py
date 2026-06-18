import pytest
from raginator.core import GeneratedAnswer, StageError
from raginator.evaluate import cost_per_million_tokens, cost_per_query


def test_cost_per_query_uses_pricing_table():
    answer = GeneratedAnswer(answer="x", sources=[], tokens_used=1_000_000)
    assert cost_per_query(answer, "gpt-4o-mini") == pytest.approx(0.15)


def test_cost_per_query_supports_custom_pricing():
    answer = GeneratedAnswer(answer="x", sources=[], tokens_used=500_000)
    assert cost_per_query(answer, "custom-model", pricing={"custom-model": 1.0}) == pytest.approx(
        0.5
    )


def test_unknown_model_raises_stage_error():
    answer = GeneratedAnswer(answer="x", sources=[], tokens_used=100)
    with pytest.raises(StageError):
        cost_per_query(answer, "no-such-model")


def test_cost_per_million_tokens_lookup():
    assert cost_per_million_tokens("mistral-small-latest") == 0.20
