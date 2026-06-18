# core 🧩 — shared interfaces

Not a pipeline stage itself — this is the contract every other stage implements,
plus the data types that flow between them. Every other `raginator/<stage>/`
package depends on `raginator.core`; it depends on nothing else in this repo.

## Interfaces (`raginator.core.base`)

| Interface  | Stage | Abstract method                                              |
|------------|-------|----------------------------------------------------------------|
| `Ingestor`  | 0 | `ingest() -> Iterable[RawDocument]` |
| `Chunker`   | 1 | `chunk(document: RawDocument) -> list[Chunk]` |
| `Embedder`  | 2 | `embed_texts(texts: list[str]) -> list[list[float]]` (plus a concrete `embed_chunks()` convenience wrapper) |
| `VectorStore` | 3 | `add(embedded_chunk)`, `search(query_embedding, top_k) -> list[RetrievedChunk]` |
| `Retriever` | 4 | `retrieve(query, top_k) -> list[RetrievedChunk]` (plus a concrete no-op `index(chunks)` hook — see below) |
| `Reranker`  | 5 | `rerank(query, candidates) -> list[RetrievedChunk]` |
| `Generator` | 6 | `generate(query, context) -> GeneratedAnswer` |
| `Evaluator` | 7 | `evaluate(query, answer, context) -> float` |
| `Observer`  | 8 | `record(event: str, **data) -> None` |

**`Retriever.index(chunks)`** defaults to a no-op — dense retrievers get their
data from the `VectorStore` instead. Retrievers that need their own corpus
(e.g. BM25) override it; `Pipeline.index()` (see `raginator/pipeline/`) calls
it for every batch of chunks automatically, so the orchestrator never has to
special-case retriever architecture.

## Data flow types (`raginator.core.types`)

```
RawDocument -> [Chunker] -> Chunk -> [Embedder] -> EmbeddedChunk -> [VectorStore]
                                                                          |
GeneratedAnswer <- [Generator] <- RetrievedChunk <- [Reranker] <- [Retriever]
```

| Type | Fields |
|------|--------|
| `RawDocument` | `content`, `metadata`, `source_id` |
| `Chunk` | `content`, `metadata`, `chunk_id`, `doc_id` |
| `EmbeddedChunk` | `chunk`, `embedding`, `provider` |
| `RetrievedChunk` | `chunk`, `score`, `rank` |
| `GeneratedAnswer` | `answer`, `sources`, `tokens_used=0`, `cost_usd=0.0`, `latency_ms=0.0` |

## Config (`raginator.core.config.Settings`)

A `pydantic-settings` `BaseSettings` (env prefix `RAGINATOR_`, also reads
`.env`) holding the keys/URLs every provider implementation falls back to
when not passed an explicit constructor argument:

```
RAGINATOR_OPENAI_API_KEY
RAGINATOR_MISTRAL_API_KEY
RAGINATOR_HUGGINGFACE_API_KEY
RAGINATOR_OLLAMA_BASE_URL      (default: http://localhost:11434)
RAGINATOR_GITHUB_TOKEN
RAGINATOR_POSTGRES_DSN
RAGINATOR_PINECONE_API_KEY
RAGINATOR_CHUNK_SIZE           (default: 200)
RAGINATOR_CHUNK_OVERLAP        (default: 50)
RAGINATOR_EMBEDDING_DIM        (default: 256)
RAGINATOR_TOP_K                (default: 5)
```

## Exceptions (`raginator.core.exceptions`)

`RaginatorError` is the base; `StageError(stage, message)` is raised by
provider implementations (e.g. a missing API key) and carries which stage
raised it.

## Tests

```bash
./go test core
```
