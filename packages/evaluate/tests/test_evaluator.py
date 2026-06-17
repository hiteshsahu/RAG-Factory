from ragfactory.evaluate import KeywordOverlapEvaluator


def test_full_keyword_overlap_scores_one():
    score = KeywordOverlapEvaluator().evaluate("raginator tri state", "raginator tri state", [])
    assert score == 1.0


def test_no_overlap_scores_zero():
    score = KeywordOverlapEvaluator().evaluate("raginator", "completely unrelated", [])
    assert score == 0.0
