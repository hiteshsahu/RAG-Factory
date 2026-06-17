from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Pipeline-wide settings, overridable via RAGFACTORY_* env vars or a .env file."""

    model_config = SettingsConfigDict(env_prefix="RAGFACTORY_", env_file=".env", extra="ignore")

    openai_api_key: str | None = None
    github_token: str | None = None
    chunk_size: int = 200
    chunk_overlap: int = 50
    embedding_dim: int = 256
    top_k: int = 5
