# Stage 1 — Chunk 📑

**The Chunk-Inator**

Slices a `RawDocument` into retrievable `Chunk`s.

## Interface

```python
class Chunker(ABC):
    def chunk(self, document: RawDocument) -> list[Chunk]: ...
```

## Implementations

| Class | Strategy | Notes |
|-------|----------|-------|
| `FixedSizeChunker(chunk_size=200, overlap=50)` | fixed-size sliding window | toy default |
| `RecursiveChunker(chunk_size=200, overlap=50, separators=None)` | splits on a separator hierarchy (paragraphs → sentences → words by default), then merges small pieces back up to `chunk_size` | pure stdlib |
| `SemanticChunker(embedder: Embedder, breakpoint_threshold=0.5)` | embeds each sentence, splits where adjacent-sentence similarity drops below the threshold | needs an injected `Embedder` (any stage-2 implementation) |
| `CodeChunker()` | splits Python source by top-level `def`/`class` via `ast`; falls back to blank-line-delimited blocks for non-Python | pure stdlib |

All four are pure-Python/stdlib — `raginator[chunk]` has no third-party deps
beyond `core`.

## Usage

```python
from raginator.chunk import FixedSizeChunker
from raginator.core import RawDocument

doc = RawDocument(content="...", metadata={}, source_id="doc-1")
chunks = FixedSizeChunker(chunk_size=200, overlap=50).chunk(doc)
```

## Tests

```bash
./go test chunk
```
