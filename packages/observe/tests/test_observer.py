import logging

from ragfactory.observe import LoggingObserver


def test_record_logs_event_and_data(caplog):
    with caplog.at_level(logging.INFO, logger="ragfactory"):
        LoggingObserver().record("indexed", chunk_count=3)

    assert "indexed" in caplog.text
    assert "chunk_count" in caplog.text
