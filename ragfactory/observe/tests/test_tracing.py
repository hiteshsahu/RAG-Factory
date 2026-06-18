from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from ragfactory.observe import OpenTelemetryObserver


def _tracer_with_exporter():
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return provider.get_tracer("test"), exporter


def test_record_opens_a_span_when_none_is_active():
    tracer, exporter = _tracer_with_exporter()

    OpenTelemetryObserver(tracer=tracer).record("indexed", chunk_count=3)

    [span] = exporter.get_finished_spans()
    assert span.name == "indexed"
    assert span.attributes["chunk_count"] == 3


def test_record_adds_event_to_active_span():
    tracer, exporter = _tracer_with_exporter()

    with tracer.start_as_current_span("parent"):
        OpenTelemetryObserver(tracer=tracer).record("query", question="hi", score=0.5)

    [span] = exporter.get_finished_spans()
    assert span.name == "parent"
    [event] = span.events
    assert event.name == "query"
    assert event.attributes["question"] == "hi"
    assert event.attributes["score"] == 0.5
