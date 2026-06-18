from __future__ import annotations

from typing import Any

import requests
from raginator.core import Reranker, RetrievedChunk, Settings, StageError

HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/{model}"


class CrossEncoderReranker(Reranker):
    """Reranks candidates via a cross-encoder model on the HuggingFace Inference
    API (The Better-Find-Inator, cross-encoder mode).

    Cross-encoders score a (query, document) pair jointly in one forward pass,
    typically more accurate than comparing independent embeddings, at the
    cost of one scored pair per candidate instead of a single vector lookup.
    """

    def __init__(
        self,
        model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._model = model
        self._api_key = api_key if api_key is not None else Settings().huggingface_api_key
        self._timeout = timeout

    def rerank(self, query: str, candidates: list[RetrievedChunk]) -> list[RetrievedChunk]:
        if not candidates:
            return []
        if not self._api_key:
            raise StageError(
                "rerank",
                "HuggingFace API key not set (pass api_key= or set RAGINATOR_HUGGINGFACE_API_KEY)",
            )

        response = requests.post(
            HUGGINGFACE_API_URL.format(model=self._model),
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={"inputs": [[query, candidate.chunk.content] for candidate in candidates]},
            timeout=self._timeout,
        )
        response.raise_for_status()
        scores = [_extract_score(item) for item in response.json()]

        reranked = sorted(
            zip(candidates, scores, strict=True), key=lambda pair: pair[1], reverse=True
        )
        return [
            RetrievedChunk(chunk=candidate.chunk, score=score, rank=rank)
            for rank, (candidate, score) in enumerate(reranked)
        ]


def _extract_score(item: Any) -> float:
    if isinstance(item, list):
        return max(float(entry["score"]) for entry in item)
    if isinstance(item, dict):
        return float(item["score"])
    return float(item)
