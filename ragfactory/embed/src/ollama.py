from __future__ import annotations

import requests
from ragfactory.core import Embedder, Settings

OLLAMA_EMBEDDINGS_PATH = "/api/embeddings"


class OllamaEmbedder(Embedder):
    """Embeds text via a local Ollama server (The Embed-Inator). No API key needed."""

    provider_name = "ollama"

    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._model = model
        self._base_url = (base_url if base_url is not None else Settings().ollama_base_url).rstrip(
            "/"
        )
        self._timeout = timeout

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        response = requests.post(
            f"{self._base_url}{OLLAMA_EMBEDDINGS_PATH}",
            json={"model": self._model, "prompt": text},
            timeout=self._timeout,
        )
        response.raise_for_status()
        return response.json()["embedding"]
