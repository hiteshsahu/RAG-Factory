export const formatBytes = (b: number) =>
  b > 1_048_576 ? (b / 1_048_576).toFixed(1) + ' MB' : Math.round(b / 1024) + ' KB'

export interface Stage {
  num:   number
  name:  string
  alias: string
  stats: string
  logs:  string[]
  error: string
}

export interface SourceChunk {
  path:  string
  text:  string
  score: number
}

export interface DemoAnswer {
  q:       string
  a:       string
  sources: SourceChunk[]
  ms:      number
  tokens:  number
  cost:    string
}

export interface CorpusStats {
  docs:            number
  chunks:          number
  avgChunkTokens:  number
  embeddingModel:  string
  indexSizeBytes:  number
}

// Mirrors raginator's real stage providers (ragfactory/embed, /generate,
// /store, /chunk) so picking a provider here is more than cosmetic -- the
// model names/dims below are the actual defaults from that backend code.
export type Provider      = 'Mistral' | 'OpenAI' | 'Ollama'
export type VectorStore   = 'ChromaDB' | 'pgvector'
export type ChunkStrategy = 'Fixed' | 'Recursive' | 'Semantic' | 'Code'

export interface PipelineSettings {
  embedProvider: Provider
  vectorStore:   VectorStore
  llmProvider:   Provider
  chunkStrategy: ChunkStrategy
}

// Ollama by default -- no API key required, so the app works the moment
// Ollama is installed/running, with no signup/config step first.
export const DEFAULT_SETTINGS: PipelineSettings = {
  embedProvider: 'Ollama',
  vectorStore: 'ChromaDB',
  llmProvider: 'Ollama',
  chunkStrategy: 'Semantic',
}

export const EMBED_MODELS: Record<Provider, { name: string; dim: number }> = {
  Mistral: { name: 'mistral-embed', dim: 1024 },
  OpenAI:  { name: 'text-embedding-3-small', dim: 1536 },
  Ollama:  { name: 'nomic-embed-text', dim: 768 },
}

export const LLM_MODELS: Record<Provider, string> = {
  Mistral: 'mistral-small-latest',
  OpenAI: 'gpt-4o-mini',
  Ollama: 'llama3.2',
}

export const STAGES: Stage[] = [
  {
    num: 0, name: 'Ingest', alias: 'Suck-inator',
    stats: '247 docs · 12.4 MB',
    logs: ['Loading PDF parser…', 'Reading 247 documents…', '247 RawDocument objects extracted'],
    error: 'Failed to parse doc 142/247: corrupted PDF header (not a PDF 1.x file)',
  },
  {
    num: 1, name: 'Chunk', alias: 'Chop-inator',
    stats: '1,842 chunks · avg 312 tok',
    logs: ['Semantic chunker init…', 'Splitting documents…', '247 docs → 1,842 chunks'],
    error: 'Semantic chunker OOM: embedding batch exceeded available memory (4.2 GB)',
  },
  {
    num: 2, name: 'Embed', alias: 'Vectorize-inator',
    stats: 'dim=1024 · 1,240 chunks/sec',
    logs: ['Mistral embed API ready', 'Embedding 1,842 chunks…', 'Done'],
    error: 'Mistral embed API rate-limited (HTTP 429) after 3 retries',
  },
  {
    num: 3, name: 'Store', alias: 'Remember-inator',
    stats: 'ChromaDB · 1,842 vectors',
    logs: ['Collection created', 'Inserting vectors…', '1,842 persisted'],
    error: 'ChromaDB connection refused (ECONNREFUSED 127.0.0.1:8000) — is the server running?',
  },
  {
    num: 4, name: 'Retrieve', alias: 'Find-inator',
    stats: 'Hybrid BM25+dense · k=5',
    logs: ['BM25 index built', 'Dense index ready', 'Retriever ready'],
    error: 'BM25 index corrupted: term frequency table out of sync with corpus',
  },
  {
    num: 5, name: 'Rerank', alias: 'Better-Find-inator',
    stats: 'cross-encoder · +18% precision',
    logs: ['Loading cross-encoder…', 'Baseline p@5: 0.84', 'Reranker ready'],
    error: 'Cross-encoder model failed to load: CUDA out of memory',
  },
  {
    num: 6, name: 'Generate', alias: 'Answer-inator',
    stats: 'Mistral 7B · Self-RAG',
    logs: ['Mistral API connected', 'Self-RAG strategy loaded', 'Generator ready'],
    error: 'Mistral API timeout after 30s — no response received',
  },
  {
    num: 7, name: 'Evaluate', alias: 'Was-it-good-inator',
    stats: 'faithfulness=0.91 · p@5=0.84',
    logs: ['Running eval suite…', 'Faithfulness: 0.91', 'report.html saved'],
    error: 'Eval suite crashed: ZeroDivisionError in faithfulness scorer (empty context)',
  },
]

export const DEMO_QA: DemoAnswer[] = [
  {
    q: 'How does function calling work?',
    a: 'Mistral function calling lets you pass tool definitions alongside your prompt. The model decides when to invoke a tool and returns structured JSON with the function name and arguments. You execute the function and pass the result back as a tool message — enabling multi-step agentic workflows.',
    sources: [
      {
        path: 'docs/function-calling.md',
        score: 0.91,
        text: 'To use function calling, pass a `tools` array alongside your messages, each entry describing a function name, JSON-schema parameters, and a description. The model responds with `tool_calls` containing the function name and arguments as a JSON string — never executes the function itself. Your application runs it and appends the result as a `role: "tool"` message before calling the API again.',
      },
      {
        path: 'docs/api-reference.md',
        score: 0.78,
        text: '`POST /v1/chat/completions` accepts an optional `tools` parameter (array of `{type: "function", function: {...}}`) and `tool_choice` (`"auto"`, `"none"`, or a specific function). Responses include `choices[0].message.tool_calls` when the model elects to call a tool, with `finish_reason: "tool_calls"`.',
      },
    ],
    ms: 312, tokens: 187, cost: '$0.00021',
  },
  {
    q: 'What models does Mistral offer?',
    a: 'Mistral offers open-weight models (Mistral 7B, Mixtral 8×7B) for self-hosting, and API-only tiers: Mistral Small for cost-sensitive workloads, Mistral Medium for balanced performance, and Mistral Large as the flagship reasoning model. All support function calling and the OpenAI-compatible chat completion format.',
    sources: [
      {
        path: 'docs/models.md',
        score: 0.88,
        text: 'Open-weight: Mistral 7B (Apache 2.0, 7B params) and Mixtral 8×7B (sparse mixture-of-experts, 8 experts of 7B). API-only: Mistral Small (cost-optimized), Mistral Medium (balanced cost/performance), and Mistral Large (flagship, strongest reasoning and multilingual support). All models share the same OpenAI-compatible chat completion schema.',
      },
      {
        path: 'docs/pricing.md',
        score: 0.69,
        text: 'Mistral Small: $0.002 / 1K input tokens, $0.006 / 1K output. Mistral Medium: $0.0027 / 1K input, $0.0081 / 1K output. Mistral Large: $0.008 / 1K input, $0.024 / 1K output. Open-weight models incur no API cost when self-hosted — only your own infrastructure spend.',
      },
    ],
    ms: 289, tokens: 142, cost: '$0.00018',
  },
  {
    q: 'How do I deploy Mistral on-prem?',
    a: 'On-premises deployment is available through the enterprise tier. Run models using vLLM, TGI, or the official inference server. Mistral 7B fits on a single A100 80GB; Mixtral 8×7B needs 2–4 A100s depending on quantization. The API is OpenAI-compatible so existing tooling works without changes.',
    sources: [
      {
        path: 'docs/self-hosting.md',
        score: 0.93,
        text: 'Recommended serving stacks: vLLM (best throughput, PagedAttention), Hugging Face TGI (easiest setup), or the official `mistral-inference` reference server. Mistral 7B fp16 fits on one A100 80GB; Mixtral 8×7B needs 2 A100s in fp16 or 1 with 4-bit quantization. Both expose an OpenAI-compatible `/v1/chat/completions` endpoint.',
      },
      {
        path: 'docs/enterprise.md',
        score: 0.71,
        text: 'The enterprise tier adds on-prem and VPC-isolated deployment, a private model registry, fine-tuning support, and SLA-backed support. Self-hosted deployments retain full data residency — no requests leave your infrastructure.',
      },
    ],
    ms: 401, tokens: 201, cost: '$0.00026',
  },
]
