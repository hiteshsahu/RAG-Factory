from __future__ import annotations

import requests
from ragfactory.core import Embedder, Settings, StageError

MISTRAL_API_URL = "https://api.mistral.ai/v1/embeddings"


class MistralEmbedder(Embedder):
    """Embeds text via the Mistral AI embeddings API (The Embed-Inator, default provider)."""

    provider_name = "mistral"

    def __init__(
        self,
        model: str = "mistral-embed",
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._model = model
        self._api_key = api_key if api_key is not None else Settings().mistral_api_key
        self._timeout = timeout

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not self._api_key:
            raise StageError(
                "embed", "Mistral API key not set (pass api_key= or set RAGFACTORY_MISTRAL_API_KEY)"
            )

        response = requests.post(
            MISTRAL_API_URL,
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={"model": self._model, "input": texts},
            timeout=self._timeout,
        )
        response.raise_for_status()
        return [item["embedding"] for item in response.json()["data"]]
