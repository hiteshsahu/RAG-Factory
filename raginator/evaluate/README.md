# Stage 7 — Evaluate 📋

**The Evaluate-Inator**

Judges the pipeline's own work — both live, per-query scoring and
offline/batch metrics.

## Interface

```python
class Evaluator(ABC):
    def evaluate(self, query: str, answer: GeneratedAnswer, context: list[RetrievedChunk]) -> float: ...
```

## Live-pipeline `Evaluator`s

| Class | Notes |
|-------|-------|
| `KeywordOverlapEvaluator()` | toy default — token-overlap between query/answer/context, used by `Pipeline.query()` |
| `GenerationEvaluator()` | adapter that runs `heuristic_generation_scores()` (and optionally `llm_judge_scores()`) and averages faithfulness/relevance into one float |

## Offline / batch utilities (not `Evaluator` subclasses)

| Module | Functions | Use |
|--------|-----------|-----|
| `retrieval.py` | `precision_at_k`, `recall_at_k`, `mean_reciprocal_rank`, `retrieval_metrics(...)` | need ground-truth `relevant_ids: set[str]` per query — batch eval against a labeled set, not live queries |
| `generation.py` | `heuristic_generation_scores(query, answer, context) -> GenerationScores(faithfulness, relevance)` (dependency-free token-overlap proxy), `llm_judge_scores(...)` (uses Mistral chat completions as an LLM judge, returns the same `GenerationScores` shape) | |
| `cost.py` | `PRICING_PER_MILLION_TOKENS` (USD/1M tokens, blended — **a stale-prone snapshot, verify against each provider's current pricing page**), `cost_per_query(answer, model, pricing=None)`, `cost_per_million_tokens(model, pricing=None)` | raises `StageError` for an unknown model |
| `report.py` | `EvaluationRecord` (query + answer + retrieval_metrics + generation_scores + cost_usd), `to_json(records)`, `to_html(records)` (HTML-escaped via stdlib `html.escape`), `write_report(records, output_dir)` (writes both files) | aggregate a batch run into a shareable report |

## Usage

```python
from raginator.evaluate import KeywordOverlapEvaluator, retrieval_metrics, write_report, EvaluationRecord

score = KeywordOverlapEvaluator().evaluate(query, answer, context)

metrics = retrieval_metrics(retrieved, relevant_ids={"chunk-1", "chunk-3"}, k=5)
write_report([EvaluationRecord(query=query, answer=answer, retrieval_metrics=metrics)], "out/")
```

## Tests

```bash
./go test evaluate
```
