from __future__ import annotations

import json as json_module
from dataclasses import dataclass, field
from html import escape
from pathlib import Path
from typing import Any

from raginator.core import GeneratedAnswer

from .generation import GenerationScores


@dataclass
class EvaluationRecord:
    """One query's full evaluation: retrieval metrics, generation scores, and cost."""

    query: str
    answer: GeneratedAnswer
    retrieval_metrics: dict[str, float] = field(default_factory=dict)
    generation_scores: GenerationScores | None = None
    cost_usd: float = 0.0


def to_json(records: list[EvaluationRecord]) -> str:
    """Serializes a batch of evaluation records to a JSON string."""
    return json_module.dumps([_record_to_dict(record) for record in records], indent=2)


def to_html(records: list[EvaluationRecord]) -> str:
    """Renders a batch of evaluation records as a standalone HTML report."""
    rows = "\n".join(_record_to_html_row(record) for record in records)
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>RAG-Factory Evaluation Report</title>
<style>
table {{ border-collapse: collapse; width: 100%; font-family: sans-serif; }}
th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; }}
th {{ background: #222; color: #fff; }}
</style>
</head>
<body>
<h1>RAG-Factory Evaluation Report</h1>
<table>
<tr><th>Query</th><th>Answer</th><th>Retrieval</th><th>Faithfulness</th><th>Relevance</th><th>Cost (USD)</th></tr>
{rows}
</table>
</body>
</html>"""


def write_report(records: list[EvaluationRecord], output_dir: str | Path) -> None:
    """Writes report.json and report.html into output_dir (created if missing)."""
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "report.json").write_text(to_json(records), encoding="utf-8")
    (directory / "report.html").write_text(to_html(records), encoding="utf-8")


def _record_to_dict(record: EvaluationRecord) -> dict[str, Any]:
    return {
        "query": record.query,
        "answer": record.answer.answer,
        "sources": len(record.answer.sources),
        "tokens_used": record.answer.tokens_used,
        "latency_ms": record.answer.latency_ms,
        "retrieval_metrics": record.retrieval_metrics,
        "generation_scores": (
            {
                "faithfulness": record.generation_scores.faithfulness,
                "relevance": record.generation_scores.relevance,
            }
            if record.generation_scores
            else None
        ),
        "cost_usd": record.cost_usd,
    }


def _record_to_html_row(record: EvaluationRecord) -> str:
    retrieval = ", ".join(f"{k}={v:.2f}" for k, v in record.retrieval_metrics.items()) or "-"
    faithfulness = (
        f"{record.generation_scores.faithfulness:.2f}" if record.generation_scores else "-"
    )
    relevance = f"{record.generation_scores.relevance:.2f}" if record.generation_scores else "-"
    return (
        "<tr>"
        f"<td>{escape(record.query)}</td>"
        f"<td>{escape(record.answer.answer)}</td>"
        f"<td>{escape(retrieval)}</td>"
        f"<td>{faithfulness}</td>"
        f"<td>{relevance}</td>"
        f"<td>{record.cost_usd:.6f}</td>"
        "</tr>"
    )
