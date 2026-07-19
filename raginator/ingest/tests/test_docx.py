# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from docx import Document
from raginator.ingest import DocxIngestor


def _write_docx(path: Path, text: str) -> None:
    document = Document()
    document.add_paragraph(text)
    document.save(str(path))


def test_docx_ingestor_extracts_text(tmp_path: Path):
    _write_docx(tmp_path / "doc.docx", "Hello RAGINATOR")

    [document] = list(DocxIngestor(tmp_path).ingest())

    assert "Hello RAGINATOR" in document.content
    assert document.metadata["num_paragraphs"] == 1
    assert document.source_id == str(tmp_path / "doc.docx")
