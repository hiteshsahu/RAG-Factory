from __future__ import annotations

import time

import requests
from raginator.core import GeneratedAnswer, Generator, RetrievedChunk, Settings, StageError

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

_SYSTEM_PROMPT = (
    "Answer the question using only the provided context. "
    "If the context doesn't contain the answer, say so."
)


class MistralGenerator(Generator):
    """Generates answers via the Mistral AI chat completions API
    (The Answer-Inator, default provider)."""

    def __init__(
        self,
        model: str = "mistral-small-latest",
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._model = model
        self._api_key = api_key if api_key is not None else Settings().mistral_api_key
        self._timeout = timeout

    def generate(self, query: str, context: list[RetrievedChunk]) -> GeneratedAnswer:
        if not self._api_key:
            raise StageError(
                "generate", "Mistral API key not set (pass api_key= or set RAGINATOR_MISTRAL_API_KEY)"
            )

        start = time.monotonic()
        response = requests.post(
            MISTRAL_API_URL,
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={
                "model": self._model,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": _build_prompt(query, context)},
                ],
            },
            timeout=self._timeout,
        )
        latency_ms = (time.monotonic() - start) * 1000
        response.raise_for_status()
        data = response.json()

        return GeneratedAnswer(
            answer=data["choices"][0]["message"]["content"],
            sources=context,
            tokens_used=data.get("usage", {}).get("total_tokens", 0),
            latency_ms=latency_ms,
        )


def _build_prompt(query: str, context: list[RetrievedChunk]) -> str:
    if not context:
        return f"Question: {query}\n\n(No context was retrieved.)"
    joined = "\n---\n".join(candidate.chunk.content for candidate in context)
    return f"Context:\n{joined}\n\nQuestion: {query}"
