import json
import logging

from raginator.observe import JSONFormatter, StructuredLogObserver


def test_record_logs_event_with_structured_data(caplog):
    with caplog.at_level(logging.INFO, logger="raginator"):
        StructuredLogObserver().record("indexed", chunk_count=3)

    [record] = caplog.records
    assert record.event_data == {"chunk_count": 3}


def test_json_formatter_renders_valid_json():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="raginator",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="indexed",
        args=(),
        exc_info=None,
    )
    record.event_data = {"chunk_count": 3}

    payload = json.loads(formatter.format(record))

    assert payload["event"] == "indexed"
    assert payload["chunk_count"] == 3
    assert payload["level"] == "INFO"
