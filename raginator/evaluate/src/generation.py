from __future__ import annotations

import json
from dataclasses import dataclass

import requests
from raginator.core import Evaluator, GeneratedAnswer, RetrievedChunk, Settings, StageError

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

_JUDGE_SYSTEM_PROMPT = (
    "You are evaluating a RAG system's answer. Score two things on a 0.0-1.0 scale:\n"
    "- faithfulness: is every claim in the answer supported by the given context "
    "(1.0 = fully grounded, 0.0 = pure hallucination)?\n"
    "- relevance: does the answer actually address the question "
    "(1.0 = fully answers it, 0.0 = off-topic)?\n"
    'Respond with ONLY a JSON object: {"faithfulness": <float>, "relevance": <float>}'
)


@dataclass
class GenerationScores:
    faithfulness: float
    relevance: float


def heuristic_generation_scores(
    query: str, answer: GeneratedAnswer, context: list[RetrievedChunk]
) -> GenerationScores:
    """Dependency-free token-overlap proxy for faithfulness/relevance.

    Fast and free, but a weak stand-in for true semantic judgment -- prefer
    llm_judge_scores when an API key is available.
    """
    answer_terms = set(answer.answer.lower().split())
    query_terms = set(query.lower().split())
    context_terms = {
        term for candidate in context for term in candidate.chunk.content.lower().split()
    }

    relevance = len(answer_terms & query_terms) / len(query_terms) if query_terms else 0.0
    faithfulness = len(answer_terms & context_terms) / len(answer_terms) if answer_terms else 0.0
    return GenerationScores(faithfulness=faithfulness, relevance=relevance)


def llm_judge_scores(
    query: str,
    answer: GeneratedAnswer,
    context: list[RetrievedChunk],
    model: str = "mistral-small-latest",
    api_key: str | None = None,
    timeout: float = 30.0,
) -> GenerationScores:
    """Asks an LLM to rate faithfulness and relevance directly, instead of
    approximating them with token overlap."""
    resolved_key = api_key if api_key is not None else Settings().mistral_api_key
    if not resolved_key:
        raise StageError(
            "evaluate", "Mistral API key not set (pass api_key= or set RAGINATOR_MISTRAL_API_KEY)"
        )

    joined_context = "\n---\n".join(candidate.chunk.content for candidate in context)
    user_prompt = f"Context:\n{joined_context}\n\nQuestion: {query}\n\nAnswer: {answer.answer}"

    response = requests.post(
        MISTRAL_API_URL,
        headers={"Authorization": f"Bearer {resolved_key}"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": _JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
        },
        timeout=timeout,
    )
    response.raise_for_status()
    scores = json.loads(response.json()["choices"][0]["message"]["content"])
    return GenerationScores(
        faithfulness=float(scores["faithfulness"]), relevance=float(scores["relevance"])
    )


class GenerationEvaluator(Evaluator):
    """Adapts heuristic faithfulness/relevance scoring to the single-float
    Evaluator interface (their average), so it can be used directly in
    Pipeline.query(). Use heuristic_generation_scores/llm_judge_scores
    directly when you want the individual sub-scores (e.g. in report.py).
    """

    def evaluate(
        self, query: str, answer: GeneratedAnswer, context: list[RetrievedChunk]
    ) -> float:
        scores = heuristic_generation_scores(query, answer, context)
        return (scores.faithfulness + scores.relevance) / 2
