from __future__ import annotations

from collections.abc import Iterable

import requests
from bs4 import BeautifulSoup
from raginator.core import Ingestor, RawDocument


class WebIngestor(Ingestor):
    """Fetches each URL and extracts visible text from its HTML (The Suck-Inator)."""

    def __init__(self, urls: list[str], timeout: float = 10.0) -> None:
        self._urls = urls
        self._timeout = timeout

    def ingest(self) -> Iterable[RawDocument]:
        for url in self._urls:
            response = requests.get(url, timeout=self._timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup(["script", "style"]):
                tag.decompose()
            content = " ".join(soup.get_text(separator=" ").split())
            yield RawDocument(
                content=content,
                metadata={"url": url, "status_code": response.status_code},
                source_id=url,
            )
