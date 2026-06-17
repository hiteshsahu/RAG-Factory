from __future__ import annotations

import logging

from ragfactory.core import Observer

logger = logging.getLogger("ragfactory")


class LoggingObserver(Observer):
    """Logs pipeline events via the standard logging module (The Observe-Inator)."""

    def record(self, event: str, **data: object) -> None:
        logger.info("%s %s", event, data)
