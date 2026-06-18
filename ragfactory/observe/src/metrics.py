from __future__ import annotations

from typing import Any

from prometheus_client import CollectorRegistry, Counter, Histogram
from ragfactory.core import Observer


class PrometheusObserver(Observer):
    """Exposes pipeline events as Prometheus counters/histograms
    (The Observe-Inator, metrics mode).

    Scrape via prometheus_client's WSGI app (make_wsgi_app(registry=...)) or
    start_http_server(), pointed at this instance's registry.
    """

    def __init__(self, registry: CollectorRegistry | None = None) -> None:
        self.registry = registry if registry is not None else CollectorRegistry()
        self._index_requests = Counter(
            "ragfactory_index_requests_total",
            "Total indexing operations",
            registry=self.registry,
        )
        self._indexed_chunks = Counter(
            "ragfactory_indexed_chunks_total",
            "Total chunks indexed",
            registry=self.registry,
        )
        self._query_requests = Counter(
            "ragfactory_query_requests_total",
            "Total query operations",
            registry=self.registry,
        )
        self._query_score = Histogram(
            "ragfactory_query_score",
            "Evaluator score distribution for queries",
            registry=self.registry,
        )

    def record(self, event: str, **data: Any) -> None:
        if event == "indexed":
            self._index_requests.inc()
            self._indexed_chunks.inc(data.get("chunk_count", 0))
        elif event == "query":
            self._query_requests.inc()
            score = data.get("score")
            if score is not None:
                self._query_score.observe(score)
