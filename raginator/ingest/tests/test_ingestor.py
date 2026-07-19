# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from raginator.ingest import TextFileIngestor


def test_ingest_reads_all_text_files(tmp_path: Path):
    (tmp_path / "a.txt").write_text("first")
    (tmp_path / "b.txt").write_text("second")
    (tmp_path / "ignored.md").write_text("not picked up")

    documents = list(TextFileIngestor(tmp_path).ingest())

    assert [doc.content for doc in documents] == ["first", "second"]
    assert documents[0].source_id == str(tmp_path / "a.txt")
