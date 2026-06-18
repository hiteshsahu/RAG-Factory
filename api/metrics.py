from __future__ import annotations

from typing import Any

from raginator.core import Observer
from raginator.observe import LoggingObserver, PrometheusObserver

# Single shared instance for the bridge's lifetime -- Prometheus counters are
# cumulative, so this has to persist across pipeline runs/queries instead of
# being rebuilt per request (that would reset everything back to zero).
prometheus_observer = PrometheusObserver()


class FanOutObserver(Observer):
    """Forwards every event to multiple observers. Pipeline only takes one
    observer, but the bridge wants both stdout logging (LoggingObserver) and
    live Prometheus counters (PrometheusObserver) from the same events."""

    def __init__(self, *observers: Observer) -> None:
        self._observers = observers

    def record(self, event: str, **data: Any) -> None:
        for observer in self._observers:
            observer.record(event, **data)


def bridge_observer() -> Observer:
    return FanOutObserver(LoggingObserver(), prometheus_observer)
