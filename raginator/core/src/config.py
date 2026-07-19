# Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Pipeline-wide settings, overridable via RAGINATOR_* env vars or a .env file."""

    model_config = SettingsConfigDict(env_prefix="RAGINATOR_", env_file=".env", extra="ignore")

    openai_api_key: str | None = None
    mistral_api_key: str | None = None
    huggingface_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    github_token: str | None = None
    postgres_dsn: str | None = None
    pinecone_api_key: str | None = None
    chunk_size: int = 200
    chunk_overlap: int = 50
    embedding_dim: int = 256
    top_k: int = 5
