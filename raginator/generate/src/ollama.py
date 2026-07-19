# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import time

import requests
from raginator.core import GeneratedAnswer, Generator, RetrievedChunk, Settings

OLLAMA_CHAT_PATH = "/api/chat"

_SYSTEM_PROMPT = (
    "Answer the question using only the provided context. "
    "If the context doesn't contain the answer, say so."
)


class OllamaGenerator(Generator):
    """Generates answers via a local Ollama server (The Answer-Inator). No API key needed."""

    def __init__(
        self,
        model: str = "llama3.2",
        base_url: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self._model = model
        self._base_url = (base_url if base_url is not None else Settings().ollama_base_url).rstrip(
            "/"
        )
        self._timeout = timeout

    def generate(self, query: str, context: list[RetrievedChunk]) -> GeneratedAnswer:
        start = time.monotonic()
        response = requests.post(
            f"{self._base_url}{OLLAMA_CHAT_PATH}",
            json={
                "model": self._model,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": _build_prompt(query, context)},
                ],
                "stream": False,
            },
            timeout=self._timeout,
        )
        latency_ms = (time.monotonic() - start) * 1000
        response.raise_for_status()
        data = response.json()

        return GeneratedAnswer(
            answer=data["message"]["content"],
            sources=context,
            tokens_used=data.get("eval_count", 0) + data.get("prompt_eval_count", 0),
            latency_ms=latency_ms,
        )


def _build_prompt(query: str, context: list[RetrievedChunk]) -> str:
    if not context:
        return f"Question: {query}\n\n(No context was retrieved.)"
    joined = "\n---\n".join(candidate.chunk.content for candidate in context)
    return f"Context:\n{joined}\n\nQuestion: {query}"
