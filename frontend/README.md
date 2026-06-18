# Raginator UI

> "Behold! The RAGINATOR! Point it at ANY data source and it shall RAG-ify everything in the tri-state area!"
> — Dr. Doofenshmirtz, probably

React + TypeScript + Material UI frontend for the Raginator pipeline.

## Stack

- React 18 + TypeScript
- Material UI v5 (dark theme)
- Vite

## Setup

```bash
npm install
npm run dev
```

Open http://localhost:5173

## Project structure

```
src/
├── App.tsx               # Root — state machine (drop → process → chat)
├── main.tsx              # Entry point
├── theme/
│   └── index.ts          # MUI dark theme + component overrides
├── data/
│   └── index.ts          # Stage definitions + demo Q&A
└── components/
    ├── DropState.tsx     # State 1 — file drop + URL input
    ├── ProcessState.tsx  # State 2 — pipeline animation
    └── ChatState.tsx     # State 3 — RAG chat interface
```

## Connecting to the real Raginator backend

Replace the `sleep()` simulation in `App.tsx` `runPipeline()` with real API calls:

```ts
// App.tsx — runPipeline()
const res = await fetch('/api/ingest', {
  method: 'POST',
  body: formData,              // files
})
const { jobId } = await res.json()

// Poll or SSE for stage progress
const stream = new EventSource(`/api/jobs/${jobId}/progress`)
stream.onmessage = (e) => {
  const { stage, log, done } = JSON.parse(e.data)
  addLog(log)
  if (done) setStagesDone(stage + 1)
}
```

Replace the mock answers in `ChatState.tsx` `sendMessage()`:

```ts
const res = await fetch('/api/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: text, corpusId }),
})
const { answer, sources, ms, tokens, cost } = await res.json()
```

## Self-destruct

```bash
# "Curse you, Perry the Platypus!"
rm -rf node_modules dist
```
