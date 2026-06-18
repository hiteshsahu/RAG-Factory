from pathlib import Path

from raginator.ingest import PDFIngestor
from reportlab.pdfgen import canvas


def _write_pdf(path: Path, text: str) -> None:
    c = canvas.Canvas(str(path))
    c.drawString(72, 700, text)
    c.save()


def test_pdf_ingestor_extracts_text(tmp_path: Path):
    _write_pdf(tmp_path / "doc.pdf", "Hello RAGINATOR")

    [document] = list(PDFIngestor(tmp_path).ingest())

    assert "Hello RAGINATOR" in document.content
    assert document.metadata["num_pages"] == 1
    assert document.source_id == str(tmp_path / "doc.pdf")
