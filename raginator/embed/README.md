# Stage 2 — Embed 🔢

**The Embed-Inator**

Converts chunk text (or a raw query string) into vector embeddings.

## Interface

```python
class Embedder(ABC):
    provider_name: str = "unknown"
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...
    def embed_chunks(self, chunks: list[Chunk]) -> list[EmbeddedChunk]:  # concrete, calls embed_texts
```

`embed_chunks()` is the indexing-flow convenience (Stage 2 → Stage 3); query
embedding (Stage 4) calls `embed_texts()` directly since a query isn't a `Chunk`.

## Implementations

| Class | Provider | Default model | Notes |
|-------|----------|----------------|-------|
| `HashingEmbedder(dim=256)` | none | — | toy default: deterministic hash-based vectors, no network/model |
| `MistralEmbedder(model="mistral-embed", api_key=None, timeout=30.0)` | Mistral API | `mistral-embed` | default real provider |
| `OpenAIEmbedder(model="text-embedding-3-small", api_key=None, timeout=30.0)` | OpenAI API | `text-embedding-3-small` | |
| `HuggingFaceEmbedder(model="sentence-transformers/all-MiniLM-L6-v2", api_key=None, timeout=30.0)` | HF Inference API | `all-MiniLM-L6-v2` | hosted inference, not local `sentence-transformers` |
| `OllamaEmbedder(model="nomic-embed-text", base_url=None, timeout=30.0)` | local Ollama server | `nomic-embed-text` | no API key needed |

`api_key=None` falls back to `Settings()` (`RAGINATOR_MISTRAL_API_KEY`,
`RAGINATOR_OPENAI_API_KEY`, `RAGINATOR_HUGGINGFACE_API_KEY`); missing keys
raise `StageError`. `base_url=None` on `OllamaEmbedder` falls back to
`RAGINATOR_OLLAMA_BASE_URL` (default `http://localhost:11434`).

## Running Ollama locally

`OllamaEmbedder` needs a running Ollama server with the embedding model
already pulled -- it doesn't pull models on demand, so a missing model fails
with a `404 Not Found` on `/api/embeddings`, not a clear "model missing"
error.

```bash
brew install ollama          # or download from https://ollama.com
ollama serve                 # starts the server on :11434 (skip if already running)
ollama pull nomic-embed-text # default model OllamaEmbedder expects
ollama list                  # confirm it's there
```

If you're also using `OllamaGenerator` (Stage 6) against the same server,
pull its model too (default `llama3.2`):

```bash
ollama pull llama3.2
```

## Usage

```python
from raginator.embed import HashingEmbedder

vectors = HashingEmbedder(dim=64).embed_texts(["hello world"])
```

## Install

```bash
./go install embed   # numpy, requests
```

## Tests

```bash
./go test embed
```
