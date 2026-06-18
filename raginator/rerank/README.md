# Stage 5 — Rerank 🔀

**The Better-Find-Inator**

Reorders retrieved candidates by relevance before they go to generation.

## Interface

```python
class Reranker(ABC):
    def rerank(self, query: str, candidates: list[RetrievedChunk]) -> list[RetrievedChunk]: ...
```

## Implementations

| Class | Provider | Default model | Notes |
|-------|----------|----------------|-------|
| `IdentityReranker()` | none | — | toy default, passthrough that preserves retrieval order |
| `CrossEncoderReranker(model="cross-encoder/ms-marco-MiniLM-L-6-v2", api_key=None, timeout=30.0)` | HF Inference API | `ms-marco-MiniLM-L-6-v2` | `api_key=None` falls back to `RAGINATOR_HUGGINGFACE_API_KEY` |
| `MistralReranker(model="mistral-rerank-v1", api_key=None, timeout=30.0)` | Mistral rerank API | `mistral-rerank-v1` | modeled on the shared rerank API shape (query + documents + top_n → relevance scores); the exact endpoint/model id wasn't independently verified against Mistral's docs at the time this was written |

`api_key=None` on either provider falls back to `Settings()`; a missing key
raises `StageError`.

## Usage

```python
from raginator.rerank import IdentityReranker

reranked = IdentityReranker().rerank("query", candidates)
```

## Tests

```bash
./go test rerank
```
