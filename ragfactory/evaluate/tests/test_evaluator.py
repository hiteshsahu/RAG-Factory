from ragfactory.core import GeneratedAnswer
from ragfactory.evaluate import KeywordOverlapEvaluator


def test_full_keyword_overlap_scores_one():
    answer = GeneratedAnswer(answer="raginator tri state", sources=[])

    score = KeywordOverlapEvaluator().evaluate("raginator tri state", answer, [])

    assert score == 1.0


def test_no_overlap_scores_zero():
    answer = GeneratedAnswer(answer="completely unrelated", sources=[])

    score = KeywordOverlapEvaluator().evaluate("raginator", answer, [])

    assert score == 0.0
