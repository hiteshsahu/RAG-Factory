# pipeline 🎛️ — wires all 9 stages together

Not one of the 9 "Inator" stages itself — this is the orchestrator that wires
a concrete implementation of every interface in `raginator.core` into a
runnable, type-safe pipeline.

## `Pipeline`

```python
class Pipeline:
    def __init__(self, ingestor, chunker, embedder, store, retriever,
                 reranker, generator, evaluator, observer,
                 default_top_k: int = 5) -> None: ...

    def index(self) -> int: ...                                   # ingest -> chunk -> retriever.index() -> embed -> store, returns chunk count
    def query(self, question: str, top_k: int | None = None) -> GeneratedAnswer: ...  # retrieve -> rerank -> generate -> evaluate -> observe
```

Every dependency is passed in by the caller — `Pipeline` itself doesn't import
any concrete stage implementation, so wiring in real providers (Mistral,
Chroma, pgvector, ...) is just constructor arguments.

## `Pipeline.from_config()`

```python
@classmethod
def from_config(cls, config: PipelineConfig | None = None) -> Self: ...
```

Builds the dependency-free default/toy stack (`TextFileIngestor`,
`FixedSizeChunker`, `HashingEmbedder`, `InMemoryVectorStore`,
`DenseRetriever`, `IdentityReranker`, `TemplateGenerator`,
`KeywordOverlapEvaluator`, `LoggingObserver`), tuned by `PipelineConfig`. The
concrete classes are imported lazily inside the method, so importing bare
`Pipeline` doesn't pull in every other stage's third-party deps.

## `PipelineConfig`

`pydantic-settings`, env prefix `RAGINATOR_PIPELINE_`. Tunable knobs only —
not a provider-selection registry; construct a `Pipeline` directly to swap in
real providers.

```
source_dir       (default: ".")
chunk_size       (default: 200)
chunk_overlap    (default: 50)
embedding_dim    (default: 256)
top_k            (default: 5)   # becomes Pipeline's default_top_k, used when query(top_k=None)
```

## Usage

```python
from raginator.pipeline import Pipeline, PipelineConfig

pipeline = Pipeline.from_config(PipelineConfig(source_dir="./docs"))
pipeline.index()
answer = pipeline.query("What does the RAGINATOR do?")
```

Or wire real providers directly:

```python
from raginator.embed import MistralEmbedder
from raginator.store import ChromaVectorStore
from raginator.retrieve import DenseRetriever
# ... etc
pipeline = Pipeline(ingestor=..., chunker=..., embedder=MistralEmbedder(), store=ChromaVectorStore(), ...)
```

## Tests

```bash
./go test pipeline
```
