# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from raginator.core import Evaluator, GeneratedAnswer, RetrievedChunk


class KeywordOverlapEvaluator(Evaluator):
    """Scores an answer by the fraction of query keywords it contains (The Evaluate-Inator)."""

    def evaluate(
        self, query: str, answer: GeneratedAnswer, context: list[RetrievedChunk]
    ) -> float:
        query_terms = set(query.lower().split())
        if not query_terms:
            return 0.0
        answer_terms = set(answer.answer.lower().split())
        return len(query_terms & answer_terms) / len(query_terms)
