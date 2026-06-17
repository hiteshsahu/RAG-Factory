from pathlib import Path

from ragfactory.ingest import TextFileIngestor


def test_ingest_reads_all_text_files(tmp_path: Path):
    (tmp_path / "a.txt").write_text("first")
    (tmp_path / "b.txt").write_text("second")
    (tmp_path / "ignored.md").write_text("not picked up")

    documents = list(TextFileIngestor(tmp_path).ingest())

    assert documents == ["first", "second"]
