from __future__ import annotations


class RAGFactoryError(Exception):
    """Base exception for all RAG-Factory errors."""


class StageError(RAGFactoryError):
    """Raised when a pipeline stage fails to process its input."""

    def __init__(self, stage: str, message: str) -> None:
        self.stage = stage
        super().__init__(f"[{stage}] {message}")
