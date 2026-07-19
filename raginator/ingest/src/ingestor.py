# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from raginator.core import Ingestor, RawDocument


class TextFileIngestor(Ingestor):
    """Reads every .txt file under a directory as a raw document (The Suck-Inator)."""

    def __init__(self, source_dir: str | Path) -> None:
        self._source_dir = Path(source_dir)

    def ingest(self) -> Iterable[RawDocument]:
        for path in sorted(self._source_dir.glob("*.txt")):
            yield RawDocument(
                content=path.read_text(encoding="utf-8"),
                metadata={"path": str(path)},
                source_id=str(path),
            )
