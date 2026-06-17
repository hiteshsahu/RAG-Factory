# RAG FACTORY 🦆
> Transforms chaotic PDFs, docs, websites, and APIs into trusted answers using embeddings, retrieval, reranking, and LLMs.


### Powered by the **Raginator-3000**

```python
            ┌─────────────────────────────────────┐
            │  RAGINATOR — TRI-STATE RAG MACHINE  │
            │  Patent Pending — Doofenshmirtz Inc │
            └─────────────────────────────────────┘

            "Behold! The RAGINATOR!"
             Point it at ANY data source and it shall RAG-ify everything in the tri-state area!
                                                                    — Dr. Doofenshmirtz, probably
```

![Raginator-3000](./img/cover.png)

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![CUDA](https://img.shields.io/badge/CUDA-Enabled-76B900)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00)
![C++17](https://img.shields.io/badge/C++-17-blue)
![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)

## RAG PIPELINE

![](./img/pipeline.jpeg)

### Stages

| Stage | Normal Name   | Raginator Name             | Job                                              |
|-------|---------------|----------------------------|--------------------------------------------------|
| 0     | Ingest        | **The Suck-Inator**        | Vacuums up PDFs, websites, docs, and APIs.       |
| 1     | Chunk         | **The Chunk-Inator**       | Slices knowledge into chunks.                    |
| 2     | Embed         | **The Embed-Inator**       | Converts chunks into embeddings.                 |
| 3     | Store / Index | **The Store-Inator**       | Stores everything for future evil use.           |
| 4     | Retrieve      | **The Find-Inator**        | Retrieves relevant context.                      |
| 5     | Rerank        | **The Better-Find-Inator** | Decides which context is actually useful.        |
| 6     | Generate      | **The Answer-Inator**      | Generates a response.                            |
| 7     | Evaluate      | **The Evaluate-Inator**    | judges its own work.                             |
| 8     | Observe       | **The Observe-Inator**     | Monitors the entire operation from headquarters. |



---

## 📂 Project Layout

```text
RAG-Factory/
├── packages/                    # one independently installable project per stage
│   ├── core/                    # ragfactory-core — shared abstract interfaces
│   │   └── src/ragfactory/core/base.py
│   ├── ingest/                  # ragfactory-ingest    — Stage 0, The Suck-Inator
│   ├── chunk/                   # ragfactory-chunk     — Stage 1, The Chunk-Inator
│   ├── embed/                   # ragfactory-embed     — Stage 2, The Embed-Inator
│   ├── store/                   # ragfactory-store     — Stage 3, The Store-Inator
│   ├── retrieve/                # ragfactory-retrieve  — Stage 4, The Find-Inator
│   ├── rerank/                  # ragfactory-rerank    — Stage 5, The Better-Find-Inator
│   ├── generate/                # ragfactory-generate  — Stage 6, The Answer-Inator
│   ├── evaluate/                # ragfactory-evaluate  — Stage 7, The Evaluate-Inator
│   ├── observe/                 # ragfactory-observe   — Stage 8, The Observe-Inator
│   └── pipeline/                # ragfactory-pipeline  — orchestrator wiring all 9 stages
│       (each package/<stage>/ has its own pyproject.toml, deps, ruff/mypy/pytest
│        config, src/ragfactory/<stage>/, and tests/ — ownable by a different team)
├── native/                      # optional C++/CUDA acceleration (own CMake build)
│   ├── CMakeLists.txt           # USE_CUDA=OFF by default (builds CPU-only)
│   ├── include/similarity.hpp
│   ├── src/similarity.cpp       # CPU cosine similarity
│   ├── src/similarity_cuda.cu   # CUDA kernel (built when -DUSE_CUDA=ON)
│   └── bindings/bindings.cpp    # pybind11 module: ragfactory_native
├── go                            # CLI entrypoint — ./go install | dev | test | ...
├── scripts/demo.py               # toy pipeline run by `./go demo`
├── img/
├── pyproject.toml                # root meta-package: extras + workspace tooling defaults
├── LICENSE
└── README.md
```

All packages share the `ragfactory.*` namespace (PEP 420 namespace packages)
but ship as separate distributions, each ownable by a different team — e.g.
`pip install ragfactory-chunk` pulls in only `ragfactory-core` + that stage's
own deps, not the whole monorepo.

---

### `./go` CLI

```bash
./go                      # interactive command menu
./go install_tools        # create .venv, upgrade pip
./go install              # editable-install every package, core -> stages -> pipeline
./go install chunk        # editable-install just ragfactory-core + ragfactory-chunk

```

```bash
./go dev                  # install everything, then run the toy pipeline once
./go demo                 # run the toy pipeline against sample text (no install)
```

```bash
./go test [stage]         # pytest, across everything or one package
./go lint                 # ruff check across every package
./go typecheck            # mypy across every package
./go check                # lint + typecheck + test
```

```bash
./go build_native [--cuda]  # CMake build ragfactory_native (CPU by default)
./go clean                # remove .venv, native/build, caches
```

Equivalently, the root meta-package exposes the same selection as pip extras:

```bash
pip install -e ".[all]"     # every stage + the orchestrator
pip install -e ".[chunk]"   # just Stage 1
pip install -e ".[dev]"     # all stages + pytest, ruff, mypy
```

Each stage also runs and tests independently, e.g. `cd packages/chunk && pytest`.

The pipeline runs end-to-end with pure-Python/numpy defaults (no GPU, no
model downloads). 

`./go build_native` builds the optional C++/CUDA extension
used by `ragfactory-store`; 

if it isn't built, `InMemoryVectorStore`
transparently falls back to a numpy implementation of the same similarity
scoring.

---

*© 2026 [Hitesh Kumar Sahu](https://hiteshsahu.com) · Licensed under [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)*

