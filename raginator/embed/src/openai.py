# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import requests
from raginator.core import Embedder, Settings, StageError

OPENAI_API_URL = "https://api.openai.com/v1/embeddings"


class OpenAIEmbedder(Embedder):
    """Embeds text via the OpenAI embeddings API (The Embed-Inator)."""

    provider_name = "openai"

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._model = model
        self._api_key = api_key if api_key is not None else Settings().openai_api_key
        self._timeout = timeout

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not self._api_key:
            raise StageError(
                "embed", "OpenAI API key not set (pass api_key= or set RAGINATOR_OPENAI_API_KEY)"
            )

        response = requests.post(
            OPENAI_API_URL,
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={"model": self._model, "input": texts},
            timeout=self._timeout,
        )
        response.raise_for_status()
        return [item["embedding"] for item in response.json()["data"]]
