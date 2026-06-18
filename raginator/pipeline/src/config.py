from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class PipelineConfig(BaseSettings):
    """Tunable knobs for the default toy pipeline (Pipeline.from_config()).

    Covers only the dependency-free default stack (TextFileIngestor,
    FixedSizeChunker, HashingEmbedder, InMemoryVectorStore, DenseRetriever,
    IdentityReranker, TemplateGenerator, KeywordOverlapEvaluator,
    LoggingObserver). Construct a Pipeline directly to wire in real
    providers (Mistral, Chroma, pgvector, ...) instead.
    """

    model_config = SettingsConfigDict(
        env_prefix="RAGINATOR_PIPELINE_", env_file=".env", extra="ignore"
    )

    source_dir: str = "."
    chunk_size: int = 200
    chunk_overlap: int = 50
    embedding_dim: int = 256
    top_k: int = 5
