from __future__ import annotations

import base64
from collections.abc import Iterable
from typing import Any

import requests
from raginator.core import Ingestor, RawDocument, Settings

GITHUB_API = "https://api.github.com"


class GitHubIngestor(Ingestor):
    """Walks a repo's file tree via the GitHub API and ingests Markdown docs (The Suck-Inator)."""

    def __init__(
        self,
        owner: str,
        repo: str,
        ref: str = "HEAD",
        token: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        self._owner = owner
        self._repo = repo
        self._ref = ref
        self._token = token if token is not None else Settings().github_token
        self._timeout = timeout

    def ingest(self) -> Iterable[RawDocument]:
        tree_url = f"{GITHUB_API}/repos/{self._owner}/{self._repo}/git/trees/{self._ref}"
        response = requests.get(
            tree_url, params={"recursive": "1"}, headers=self._headers(), timeout=self._timeout
        )
        response.raise_for_status()

        for entry in response.json().get("tree", []):
            path = entry["path"]
            if entry.get("type") != "blob" or not path.lower().endswith(".md"):
                continue

            blob = requests.get(entry["url"], headers=self._headers(), timeout=self._timeout)
            blob.raise_for_status()
            yield RawDocument(
                content=self._decode_blob(blob.json()),
                metadata={"path": path, "repo": f"{self._owner}/{self._repo}"},
                source_id=f"{self._owner}/{self._repo}/{path}",
            )

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/vnd.github+json"}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        return headers

    @staticmethod
    def _decode_blob(blob: dict[str, Any]) -> str:
        return base64.b64decode(blob["content"]).decode("utf-8", errors="replace")
