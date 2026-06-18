# Stage 0 — Ingest 📚

**The Suck-Inator**

Vacuums up raw documents from a source and yields `RawDocument`s for the
chunk stage.

## Interface

```python
class Ingestor(ABC):
    def ingest(self) -> Iterable[RawDocument]: ...
```

## Implementations

| Class | Source | Notes |
|-------|--------|-------|
| `TextFileIngestor(source_dir)` | local `.txt` files | toy default, no deps beyond `core` |
| `PDFIngestor(source_dir)` | local `.pdf` files | extracts text via `pypdf` |
| `WebIngestor(urls, timeout=10.0)` | HTTP(S) pages | `requests` + `beautifulsoup4`, strips `<script>`/`<style>` |
| `GitHubIngestor(owner, repo, ref="HEAD", token=None, timeout=10.0)` | a GitHub repo | walks the repo tree API, ingests Markdown/doc files only; `token` falls back to `Settings().github_token` |
| `S3Ingestor(bucket, prefix="", client=None)` | an S3 bucket/prefix | `boto3`; pass `client=` to inject a fake/mock S3 client in tests |

## Usage

```python
from raginator.ingest import TextFileIngestor

for doc in TextFileIngestor("./docs").ingest():
    print(doc.source_id, len(doc.content))
```

## Config

```
RAGINATOR_GITHUB_TOKEN   # used by GitHubIngestor if token= isn't passed
```

## Install

```bash
./go install ingest   # pypdf, requests, beautifulsoup4, boto3
```

## Tests

```bash
./go test ingest
```
