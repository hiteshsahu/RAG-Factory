from __future__ import annotations

import hashlib

import numpy as np

from ragfactory.core import Embedder


class HashingEmbedder(Embedder):
    """Deterministic bag-of-words hashing embedder (The Embed-Inator).

    A dependency-free stand-in for a real model (e.g. sentence-transformers) so the
    pipeline runs end-to-end without downloading weights or calling an API. Swap in
    a model-backed Embedder for production use.
    """

    def __init__(self, dim: int = 256) -> None:
        self._dim = dim

    def embed(self, texts: list[str]) -> list[np.ndarray]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> np.ndarray:
        vector = np.zeros(self._dim, dtype=np.float32)
        for token in text.lower().split():
            digest = hashlib.sha1(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self._dim
            vector[index] += 1.0
        norm = np.linalg.norm(vector)
        return vector / norm if norm > 0 else vector
