from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from ragfactory.core import Observer

logger = logging.getLogger("ragfactory")


class JSONFormatter(logging.Formatter):
    """Renders each LogRecord as a single JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "event": record.getMessage(),
        }
        payload.update(getattr(record, "event_data", {}))
        return json.dumps(payload)


class StructuredLogObserver(Observer):
    """Logs pipeline events as structured JSON lines (The Observe-Inator, logging mode).

    Pair with JSONFormatter on a handler to actually emit JSON; the plain
    LoggingObserver default just logs human-readable text.
    """

    def __init__(self, logger_: logging.Logger | None = None) -> None:
        self._logger = logger_ if logger_ is not None else logger

    def record(self, event: str, **data: Any) -> None:
        self._logger.info(event, extra={"event_data": data})
