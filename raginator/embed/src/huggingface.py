from __future__ import annotations

import requests
from raginator.core import Embedder, Settings, StageError

HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/{model}"


class HuggingFaceEmbedder(Embedder):
    """Embeds text via the HuggingFace Inference API (The Embed-Inator)."""

    provider_name = "huggingface"

    def __init__(
        self,
        model: str = "sentence-transformers/all-MiniLM-L6-v2",
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._model = model
        self._api_key = api_key if api_key is not None else Settings().huggingface_api_key
        self._timeout = timeout

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not self._api_key:
            raise StageError(
                "embed",
                "HuggingFace API key not set (pass api_key= or set RAGINATOR_HUGGINGFACE_API_KEY)",
            )

        response = requests.post(
            HUGGINGFACE_API_URL.format(model=self._model),
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={"inputs": texts},
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()
