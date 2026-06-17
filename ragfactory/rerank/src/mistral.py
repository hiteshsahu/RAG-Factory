from __future__ import annotations

import requests
from ragfactory.core import Reranker, RetrievedChunk, Settings, StageError

MISTRAL_RERANK_API_URL = "https://api.mistral.ai/v1/rerank"


class MistralReranker(Reranker):
    """Reranks candidates via the Mistral AI rerank API (The Better-Find-Inator).

    Follows the request/response shape shared by most hosted rerank APIs
    (query + documents + top_n -> ranked relevance scores, the same pattern
    Cohere/Jina/Voyage use). Verify the exact endpoint and model name against
    current Mistral docs before relying on this in production -- hosted
    rerank offerings move faster than chat/embeddings APIs.
    """

    def __init__(
        self,
        model: str = "mistral-rerank-v1",
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._model = model
        self._api_key = api_key if api_key is not None else Settings().mistral_api_key
        self._timeout = timeout

    def rerank(self, query: str, candidates: list[RetrievedChunk]) -> list[RetrievedChunk]:
        if not candidates:
            return []
        if not self._api_key:
            raise StageError(
                "rerank", "Mistral API key not set (pass api_key= or set RAGFACTORY_MISTRAL_API_KEY)"
            )

        response = requests.post(
            MISTRAL_RERANK_API_URL,
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={
                "model": self._model,
                "query": query,
                "documents": [candidate.chunk.content for candidate in candidates],
                "top_n": len(candidates),
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
        results = sorted(
            response.json()["results"], key=lambda result: result["relevance_score"], reverse=True
        )

        return [
            RetrievedChunk(
                chunk=candidates[result["index"]].chunk,
                score=result["relevance_score"],
                rank=rank,
            )
            for rank, result in enumerate(results)
        ]
