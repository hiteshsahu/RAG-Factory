# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import Mock, patch

import httpx
from api.preflight import preflight
from api.schemas import PipelineSettings


def test_missing_mistral_key_is_flagged(monkeypatch):
    monkeypatch.delenv("RAGINATOR_MISTRAL_API_KEY", raising=False)
    settings = PipelineSettings(embed_provider="Mistral", llm_provider="Mistral")

    errors = preflight(settings)

    assert any("RAGINATOR_MISTRAL_API_KEY" in e for e in errors)


def test_missing_openai_key_is_flagged(monkeypatch):
    monkeypatch.delenv("RAGINATOR_OPENAI_API_KEY", raising=False)
    settings = PipelineSettings(embed_provider="OpenAI", llm_provider="Mistral")
    monkeypatch.setenv("RAGINATOR_MISTRAL_API_KEY", "test-key")

    errors = preflight(settings)

    assert any("RAGINATOR_OPENAI_API_KEY" in e for e in errors)


def test_configured_mistral_key_passes(monkeypatch):
    monkeypatch.setenv("RAGINATOR_MISTRAL_API_KEY", "test-key")
    settings = PipelineSettings(embed_provider="Mistral", llm_provider="Mistral")

    assert preflight(settings) == []


def test_unreachable_ollama_is_flagged():
    settings = PipelineSettings(embed_provider="Ollama", llm_provider="Ollama")

    with patch("api.preflight.httpx.get", side_effect=httpx.ConnectError("refused")):
        errors = preflight(settings)

    assert any("Ollama unreachable" in e for e in errors)


def test_reachable_ollama_passes():
    settings = PipelineSettings(embed_provider="Ollama", llm_provider="Ollama")

    with patch("api.preflight.httpx.get", return_value=Mock(status_code=200)):
        errors = preflight(settings)

    assert errors == []


def test_pgvector_without_dsn_is_flagged(monkeypatch):
    monkeypatch.delenv("RAGINATOR_POSTGRES_DSN", raising=False)
    monkeypatch.setenv("RAGINATOR_MISTRAL_API_KEY", "test-key")
    settings = PipelineSettings(vector_store="pgvector")

    errors = preflight(settings)

    assert any("RAGINATOR_POSTGRES_DSN" in e for e in errors)


def test_chromadb_needs_no_env(monkeypatch):
    monkeypatch.setenv("RAGINATOR_MISTRAL_API_KEY", "test-key")
    settings = PipelineSettings(vector_store="ChromaDB")

    assert preflight(settings) == []
