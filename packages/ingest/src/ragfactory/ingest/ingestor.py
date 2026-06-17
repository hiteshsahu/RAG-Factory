from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ragfactory.core import Ingestor


class TextFileIngestor(Ingestor):
    """Reads every .txt file under a directory as a raw document (The Suck-Inator)."""

    def __init__(self, source_dir: str | Path) -> None:
        self._source_dir = Path(source_dir)

    def ingest(self) -> Iterable[str]:
        for path in sorted(self._source_dir.glob("*.txt")):
            yield path.read_text(encoding="utf-8")
