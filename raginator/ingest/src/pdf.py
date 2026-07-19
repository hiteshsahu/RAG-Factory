# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from pypdf import PdfReader
from raginator.core import Ingestor, RawDocument


class PDFIngestor(Ingestor):
    """Reads every .pdf file under a directory, extracting text per page (The Suck-Inator)."""

    def __init__(self, source_dir: str | Path) -> None:
        self._source_dir = Path(source_dir)

    def ingest(self) -> Iterable[RawDocument]:
        for path in sorted(self._source_dir.glob("*.pdf")):
            reader = PdfReader(str(path))
            content = "\n\n".join(page.extract_text() or "" for page in reader.pages)
            yield RawDocument(
                content=content,
                metadata={"path": str(path), "num_pages": len(reader.pages)},
                source_id=str(path),
            )
