// Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
// SPDX-License-Identifier: Apache-2.0

import type { CorpusStats, PipelineSettings, SourceChunk } from './data'

// The bridge (api/main.py) runs on :8001 -- :8000 is metrics_server.py's
// Prometheus exposition port. Start it with `./go api`.
export const API_BASE = 'http://localhost:8001'

export interface PipelineEvent {
  type: 'log' | 'stage_done' | 'error' | 'complete' | 'preflight_failed'
  stage?: number
  text?: string
  kind?: 'default' | 'success' | 'error'
  stat?: string
  errors?: string[]
  corpusStats?: CorpusStats
  suggestedQuestions?: string[]
}

/** POSTs the dropped files + settings to /api/pipeline/start and yields each
 * SSE event as it streams in. Can't use the browser's native EventSource
 * here -- it only supports GET, and this needs to POST the files. */
export async function* streamPipelineStart(
  files: File[],
  settings: PipelineSettings,
): AsyncGenerator<PipelineEvent> {
  const formData = new FormData()
  for (const file of files) formData.append('files', file)
  formData.append('settings', JSON.stringify(settings))

  const response = await fetch(`${API_BASE}/api/pipeline/start`, { method: 'POST', body: formData })
  if (!response.ok || !response.body) {
    throw new Error(`Bridge unreachable (${response.status}) -- is './go api' running?`)
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    const events = buffer.split('\n\n')
    buffer = events.pop() ?? ''
    for (const raw of events) {
      const line = raw.trim()
      if (line.startsWith('data: ')) {
        yield JSON.parse(line.slice('data: '.length)) as PipelineEvent
      }
    }
  }
}

export interface QueryResult {
  answer: string
  sources: SourceChunk[]
  ms: number
  tokens: number
  cost: string
}

export async function queryBackend(query: string): Promise<QueryResult> {
  const response = await fetch(`${API_BASE}/api/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}) as { detail?: string })
    throw new Error(body.detail ?? `Query failed (${response.status})`)
  }
  return response.json() as Promise<QueryResult>
}
