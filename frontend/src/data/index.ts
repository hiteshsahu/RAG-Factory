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

export interface DemoAnswer {
  q:       string
  a:       string
  sources: string[]
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
    sources: ['docs/function-calling.md', 'docs/api-reference.md'],
    ms: 312, tokens: 187, cost: '$0.00021',
  },
  {
    q: 'What models does Mistral offer?',
    a: 'Mistral offers open-weight models (Mistral 7B, Mixtral 8×7B) for self-hosting, and API-only tiers: Mistral Small for cost-sensitive workloads, Mistral Medium for balanced performance, and Mistral Large as the flagship reasoning model. All support function calling and the OpenAI-compatible chat completion format.',
    sources: ['docs/models.md', 'docs/pricing.md'],
    ms: 289, tokens: 142, cost: '$0.00018',
  },
  {
    q: 'How do I deploy Mistral on-prem?',
    a: 'On-premises deployment is available through the enterprise tier. Run models using vLLM, TGI, or the official inference server. Mistral 7B fits on a single A100 80GB; Mixtral 8×7B needs 2–4 A100s depending on quantization. The API is OpenAI-compatible so existing tooling works without changes.',
    sources: ['docs/self-hosting.md', 'docs/enterprise.md'],
    ms: 401, tokens: 201, cost: '$0.00026',
  },
]
