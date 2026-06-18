from __future__ import annotations

from typing import Any

from opentelemetry import trace
from opentelemetry.trace import Tracer
from raginator.core import Observer


class OpenTelemetryObserver(Observer):
    """Records pipeline events as OpenTelemetry span events
    (The Observe-Inator, tracing mode).

    Attaches to the current active span if one exists (e.g. your app's
    request span); otherwise opens a short span just for this event. Only
    depends on opentelemetry-api -- wire up the SDK + an exporter in your
    own application, the usual library-vs-app split for OTel instrumentation.
    """

    def __init__(self, tracer: Tracer | None = None) -> None:
        self._tracer = tracer if tracer is not None else trace.get_tracer("raginator")

    def record(self, event: str, **data: Any) -> None:
        attributes = {key: _coerce(value) for key, value in data.items()}
        current_span = trace.get_current_span()
        if current_span.is_recording():
            current_span.add_event(event, attributes=attributes)
        else:
            with self._tracer.start_as_current_span(event) as span:
                span.set_attributes(attributes)


def _coerce(value: Any) -> Any:
    """OTel attributes must be str/bool/int/float or homogeneous sequences thereof."""
    if isinstance(value, str | bool | int | float):
        return value
    return str(value)
