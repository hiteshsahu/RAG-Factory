from __future__ import annotations

import httpx
from api.schemas import PipelineSettings
from raginator.core import Settings

PING_TIMEOUT = 2.0


def preflight(settings: PipelineSettings) -> list[str]:
    """Checks every provider the run will actually need *before* touching a
    single file. Empty list = safe to start. Hard-fails rather than silently
    falling back to a toy provider -- a missing key should look like a missing
    key, not a wrong answer from the wrong model."""
    errors: list[str] = []
    config = Settings()

    if "Mistral" in (settings.embed_provider, settings.llm_provider) and not config.mistral_api_key:
        errors.append(
            "RAGINATOR_MISTRAL_API_KEY not set -- switch to Ollama for local embedding/generation"
        )

    if "OpenAI" in (settings.embed_provider, settings.llm_provider) and not config.openai_api_key:
        errors.append("RAGINATOR_OPENAI_API_KEY not set")

    if "Ollama" in (settings.embed_provider, settings.llm_provider):
        try:
            httpx.get(f"{config.ollama_base_url}/api/tags", timeout=PING_TIMEOUT)
        except httpx.HTTPError:
            errors.append(
                f"Ollama unreachable at {config.ollama_base_url} -- start it with: ollama serve"
            )

    if settings.vector_store == "pgvector":
        if not config.postgres_dsn:
            errors.append("RAGINATOR_POSTGRES_DSN not set -- switch to ChromaDB")
        else:
            try:
                import psycopg

                with psycopg.connect(config.postgres_dsn, connect_timeout=int(PING_TIMEOUT)):
                    pass
            except Exception as exc:
                errors.append(f"pgvector unreachable: {exc}")

    return errors
