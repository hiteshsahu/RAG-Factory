# Stage 3 — Store / Index ↗️

**The Store-Inator**

Persists embedded chunks and serves similarity search over them.

## Interface

```python
class VectorStore(ABC):
    def add(self, embedded_chunk: EmbeddedChunk) -> None: ...
    def search(self, query_embedding: list[float], top_k: int) -> list[RetrievedChunk]: ...
```

## Implementations

| Class | Backend | Notes |
|-------|---------|-------|
| `InMemoryVectorStore()` | in-process list + cosine similarity | toy default; uses the optional `raginator_native` C++/CUDA extension if built (`./go build_native`), otherwise falls back to pure numpy transparently |
| `ChromaVectorStore(collection_name="raginator", persist_directory=None, client=None)` | Chroma | default "real" store — zero-config, runs fully in-process/local |
| `PgVectorStore(dsn=None, table="raginator_chunks", dimension=256, connection=None)` | Postgres + pgvector | `psycopg`; `dsn=None` falls back to `RAGINATOR_POSTGRES_DSN`; pass `connection=` to inject a real/fake connection in tests |
| `PineconeVectorStore(index_name, api_key=None, index=None)` | Pinecone | `api_key=None` falls back to `RAGINATOR_PINECONE_API_KEY`; pass `index=` to inject a fake index in tests |

## Usage

```python
from raginator.store import InMemoryVectorStore
from raginator.core import EmbeddedChunk, Chunk

store = InMemoryVectorStore()
store.add(EmbeddedChunk(chunk=Chunk(content="...", metadata={}, chunk_id="c1", doc_id="d1"),
                         embedding=[0.1, 0.2], provider="hashing"))
results = store.search([0.1, 0.2], top_k=5)
```

## Config

```
RAGINATOR_POSTGRES_DSN
RAGINATOR_PINECONE_API_KEY
```

## Install

```bash
./go install store   # numpy, chromadb, psycopg[binary], pinecone
```

## Tests

```bash
./go test store
```
