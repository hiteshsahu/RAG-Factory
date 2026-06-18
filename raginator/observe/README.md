# Stage 8 — Observe 📊

**The Observe-Inator**

Records pipeline events for monitoring — metrics, traces, and structured logs.

## Interface

```python
class Observer(ABC):
    def record(self, event: str, **data: Any) -> None: ...
```

`Pipeline` calls `record("indexed", chunk_count=...)` after `index()` and
`record("query", question=..., score=...)` after `query()`.

## Implementations

| Class | Backend | Notes |
|-------|---------|-------|
| `LoggingObserver()` | stdlib `print`/logging | toy default |
| `PrometheusObserver(registry=None)` | `prometheus_client` | DI'd `CollectorRegistry` (so tests don't collide on the global default registry); exposes 4 metrics — see below |
| `OpenTelemetryObserver(tracer=None)` | OpenTelemetry | adds an event to the active span if one exists, otherwise opens a short-lived span; only depends on `opentelemetry-api` (an application wires up the SDK + exporter) |
| `StructuredLogObserver(logger_=None)` + `JSONFormatter` | stdlib `logging` | renders each event as one JSON line |

### Prometheus metrics

| Metric | Type | Recorded on |
|--------|------|-------------|
| `raginator_index_requests_total` | counter | `"indexed"` event |
| `raginator_indexed_chunks_total` | counter | `"indexed"` event (incremented by `chunk_count`) |
| `raginator_query_requests_total` | counter | `"query"` event |
| `raginator_query_score` | histogram | `"query"` event (the evaluator's score) |

## Dashboard

`dashboards/raginator.json` is a ready-to-load Grafana dashboard wired to the
four metrics above (validated by `tests/test_dashboard.py`). From the repo
root:

```bash
./go metrics_server   # runs the toy pipeline on a loop, exposing :8000/metrics
./go observe           # docker/podman compose up Prometheus+Grafana, opens the dashboard
```

See the root `docker-compose.yml` and `docker/` for the Prometheus scrape
config and Grafana provisioning that auto-loads this dashboard.

## Usage

```python
from raginator.observe import PrometheusObserver

observer = PrometheusObserver()
observer.record("indexed", chunk_count=12)
```

## Install

```bash
./go install observe   # prometheus-client, opentelemetry-api
```

## Tests

```bash
./go test observe
```
