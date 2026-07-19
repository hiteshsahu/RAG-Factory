# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections.abc import Iterable

import requests
from bs4 import BeautifulSoup
from raginator.core import Ingestor, RawDocument

# Wikipedia (and several other sites) reject requests.get's default
# "python-requests/X.Y" user agent outright (403) as an anti-scraping
# measure -- a descriptive UA identifying the bot + a contact URL is what
# Wikipedia's own User-Agent policy asks for, and it satisfies everyone else too.
USER_AGENT = "RaginatorWebIngestor/1.0 (+https://github.com/HiteshSahu/RAG-Factory)"


class WebIngestor(Ingestor):
    """Fetches each URL and extracts visible text from its HTML (The Suck-Inator)."""

    def __init__(self, urls: list[str], timeout: float = 10.0) -> None:
        self._urls = urls
        self._timeout = timeout

    def ingest(self) -> Iterable[RawDocument]:
        for url in self._urls:
            response = requests.get(url, timeout=self._timeout, headers={"User-Agent": USER_AGENT})
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
