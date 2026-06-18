# Stage 4 — Retrieve 🐕

**The Find-Inator**

Finds candidate chunks relevant to a query.

## Interface

```python
class Retriever(ABC):
    def index(self, chunks: list[Chunk]) -> None: ...    # concrete no-op by default
    def retrieve(self, query: str, top_k: int) -> list[RetrievedChunk]: ...
```

`index()` is called by `Pipeline.index()` for every batch of chunks. Dense
retrieval doesn't need it (the `VectorStore` already has the data); retrievers
that need their own corpus override it.

## Implementations

| Class | Strategy | Notes |
|-------|----------|-------|
| `DenseRetriever(embedder, store)` | embeds the query, searches a `VectorStore` | thin wrapper — needs an `Embedder` + `VectorStore` instance |
| `SparseRetriever(k1=1.5, b=0.75)` | BM25, implemented from scratch (pure stdlib) | builds its own corpus via `index(chunks)`, accumulated across calls |
| `HybridRetriever(dense, sparse, alpha=0.5)` | normalized weighted combination of dense + sparse scores | wraps one `DenseRetriever` + one `SparseRetriever`; `index()` forwards to the sparse side |

## Usage

```python
from raginator.embed import HashingEmbedder
from raginator.store import InMemoryVectorStore
from raginator.retrieve import DenseRetriever, SparseRetriever, HybridRetriever

embedder = HashingEmbedder(dim=64)
store = InMemoryVectorStore()
dense = DenseRetriever(embedder, store)
sparse = SparseRetriever()
hybrid = HybridRetriever(dense, sparse, alpha=0.5)
```

## Tests

```bash
./go test retrieve
```
