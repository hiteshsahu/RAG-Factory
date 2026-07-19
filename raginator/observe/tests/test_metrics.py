# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from prometheus_client import CollectorRegistry
from raginator.observe import PrometheusObserver


def test_indexed_event_increments_counters():
    registry = CollectorRegistry()
    observer = PrometheusObserver(registry=registry)

    observer.record("indexed", chunk_count=5)

    assert registry.get_sample_value("raginator_index_requests_total") == 1.0
    assert registry.get_sample_value("raginator_indexed_chunks_total") == 5.0


def test_query_event_records_score_histogram():
    registry = CollectorRegistry()
    observer = PrometheusObserver(registry=registry)

    observer.record("query", question="q", score=0.8)

    assert registry.get_sample_value("raginator_query_requests_total") == 1.0
    assert registry.get_sample_value("raginator_query_score_count") == 1.0
    assert registry.get_sample_value("raginator_query_score_sum") == 0.8


def test_unknown_event_is_ignored():
    registry = CollectorRegistry()
    observer = PrometheusObserver(registry=registry)

    observer.record("something_else", foo="bar")

    assert registry.get_sample_value("raginator_index_requests_total") == 0.0
