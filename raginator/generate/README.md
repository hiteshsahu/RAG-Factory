# Stage 6 — Generate 🧠

**The Answer-Inator**

Produces a final answer from a query and its retrieved/reranked context.

## Interface

```python
class Generator(ABC):
    def generate(self, query: str, context: list[RetrievedChunk]) -> GeneratedAnswer: ...
```

## Implementations

| Class | Provider | Default model | Notes |
|-------|----------|----------------|-------|
| `TemplateGenerator()` | none | — | toy default: templates the context straight into an answer string, no LLM call |
| `MistralGenerator(model="mistral-small-latest", api_key=None, timeout=30.0)` | Mistral chat API | `mistral-small-latest` | default real provider |
| `OpenAIGenerator(model="gpt-4o-mini", api_key=None, timeout=30.0)` | OpenAI chat API | `gpt-4o-mini` | |
| `OllamaGenerator(model="llama3.2", base_url=None, timeout=60.0)` | local Ollama server | `llama3.2` | no API key needed, longer default timeout |

All three real providers populate `GeneratedAnswer.tokens_used` and
`latency_ms`; `cost_usd` is left at `0.0` — use
`raginator.evaluate.cost_per_query()` to estimate cost separately, since
pricing is provider/model-specific and changes independently of generation.

`api_key=None` falls back to `Settings()` (`RAGINATOR_MISTRAL_API_KEY`,
`RAGINATOR_OPENAI_API_KEY`); `base_url=None` on `OllamaGenerator` falls back
to `RAGINATOR_OLLAMA_BASE_URL`.

## Usage

```python
from raginator.generate import TemplateGenerator

answer = TemplateGenerator().generate("What is X?", context=retrieved_chunks)
print(answer.answer, answer.sources)
```

## Tests

```bash
./go test generate
```
