from __future__ import annotations

from ragfactory.core import Evaluator


class KeywordOverlapEvaluator(Evaluator):
    """Scores an answer by the fraction of query keywords it contains (The Evaluate-Inator)."""

    def evaluate(self, query: str, answer: str, context: list[str]) -> float:
        query_terms = set(query.lower().split())
        if not query_terms:
            return 0.0
        answer_terms = set(answer.lower().split())
        return len(query_terms & answer_terms) / len(query_terms)
