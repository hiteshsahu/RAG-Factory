# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

import json
from pathlib import Path

from raginator.core import GeneratedAnswer
from raginator.evaluate import EvaluationRecord, GenerationScores, to_html, to_json, write_report


def _record() -> EvaluationRecord:
    answer = GeneratedAnswer(answer="<b>raginator</b>", sources=[], tokens_used=10)
    return EvaluationRecord(
        query="what is it?",
        answer=answer,
        retrieval_metrics={"precision_at_k": 1.0},
        generation_scores=GenerationScores(faithfulness=0.9, relevance=0.8),
        cost_usd=0.001,
    )


def test_to_json_round_trips_key_fields():
    data = json.loads(to_json([_record()]))

    assert data[0]["query"] == "what is it?"
    assert data[0]["generation_scores"]["faithfulness"] == 0.9
    assert data[0]["cost_usd"] == 0.001


def test_to_html_escapes_content():
    html = to_html([_record()])

    assert "<b>raginator</b>" not in html
    assert "&lt;b&gt;raginator&lt;/b&gt;" in html


def test_write_report_creates_both_files(tmp_path: Path):
    write_report([_record()], tmp_path)

    assert (tmp_path / "report.json").exists()
    assert (tmp_path / "report.html").exists()
