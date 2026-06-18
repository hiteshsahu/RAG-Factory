import React, { useCallback, useMemo, useRef, useState } from 'react'
import {
  AppBar, Box, Chip, CircularProgress,
  CssBaseline, IconButton, ThemeProvider, Toolbar, Typography,
} from '@mui/material'
import type { PaletteMode } from '@mui/material'
import LightModeIcon from '@mui/icons-material/LightMode'
import DarkModeIcon from '@mui/icons-material/DarkMode'
import getTheme from './theme'
import {
  STAGES, formatBytes, DEFAULT_SETTINGS, EMBED_MODELS, LLM_MODELS,
  type CorpusStats, type PipelineSettings,
} from './data'
import DropState from './components/DropState'
import ProcessState from './components/ProcessState'
import ChatState from './components/ChatState'
import SettingsDrawer from './components/SettingsDrawer'

type AppState = 'drop' | 'process' | 'chat'

interface LogLine { text: string; kind: 'default' | 'success' | 'error' }

const sleep = (ms: number) => new Promise(r => setTimeout(r, ms))

// Demo-only: simulates real pipelines failing partway through, so the UI's
// error handling is actually exercised instead of always happy-pathing.
const FAILURE_RATE = 0.3
const FALLBACK_CORPUS_STATS: CorpusStats = {
  docs: 0, chunks: 0, avgChunkTokens: 0,
  embeddingModel: `${EMBED_MODELS.Mistral.name} · ${EMBED_MODELS.Mistral.dim}-dim`,
  indexSizeBytes: 0,
}

export default function App() {
  const [appState, setAppState]     = useState<AppState>('drop')
  const [stagesDone, setStagesDone] = useState(0)
  const [activeStage, setActiveStage] = useState(-1)
  const [failedStage, setFailedStage] = useState<number | null>(null)
  const [logs, setLogs]             = useState<LogLine[]>([])
  const [stageStats, setStageStats] = useState<Record<number, string>>({})
  const [corpusStats, setCorpusStats] = useState<CorpusStats | null>(null)
  const [corpusName, setCorpusName] = useState('')
  const [settings, setSettings] = useState<PipelineSettings>(DEFAULT_SETTINGS)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [mode, setMode] = useState<PaletteMode>('dark')
  const theme = useMemo(() => getTheme(mode), [mode])
  const cancelRef = useRef(false)
  const lastRunRef = useRef<{ files: File[]; urls: string[] }>({ files: [], urls: [] })

  const addLog = useCallback((text: string, kind: LogLine['kind'] = 'default') => {
    setLogs(l => [...l, { text, kind }])
  }, [])

  const runPipeline = useCallback(async (files: File[], urls: string[]) => {
    cancelRef.current = false
    lastRunRef.current = { files, urls }
    const name = files.length
      ? files[0].name.replace(/\.[^.]+$/, '')
      : new URL(urls[0]).hostname
    setCorpusName(name)
    setAppState('process')
    setStagesDone(0)
    setActiveStage(0)
    setFailedStage(null)
    setLogs([])

    // Real numbers from whatever was actually dropped, not the canned demo
    // stats -- only Stage 0 gets to know the real file names/sizes, so its
    // log lines and "Nx files · Y MB" stat reflect the real input. The doc
    // count then gets substituted into the rest of the (still-scripted)
    // pipeline so the same number shows up consistently downstream.
    const itemCount = files.length || urls.length || 1
    const totalBytes = files.reduce((sum, f) => sum + f.size, 0)
    const sourceLabel = files.length
      ? `${files.length} file${files.length === 1 ? '' : 's'} · ${formatBytes(totalBytes)}`
      : `${urls.length} URL${urls.length === 1 ? '' : 's'}`

    // Chunks/index size are derived from the real byte count (~1.4 KB of
    // text per chunk) rather than a fixed demo number, so they scale with
    // whatever was actually dropped. URLs have no real byte count to read,
    // so fall back to a per-page estimate.
    const estimatedBytes = files.length ? totalBytes : urls.length * 50_000
    const chunkCount = Math.max(itemCount, Math.round(estimatedBytes / 1400))
    const avgChunkTokens = 312
    const embedModel = EMBED_MODELS[settings.embedProvider]
    const newCorpusStats: CorpusStats = {
      docs: itemCount,
      chunks: chunkCount,
      avgChunkTokens,
      embeddingModel: `${embedModel.name} · ${embedModel.dim}-dim`,
      indexSizeBytes: chunkCount * embedModel.dim * 4, // float32 vectors
    }

    const ingestLogs = files.length
      ? [
          'Loading PDF parser…',
          ...files.map(f => `Reading ${f.name} (${formatBytes(f.size)})…`),
          `${itemCount} RawDocument object${itemCount === 1 ? '' : 's'} extracted`,
        ]
      : [
          'Resolving URL(s)…',
          ...urls.map(u => `Fetching ${u}…`),
          `${itemCount} RawDocument object${itemCount === 1 ? '' : 's'} extracted`,
        ]

    // Per-stage overrides driven by the chosen settings, so picking a
    // provider in the drawer actually changes what the run shows -- not
    // just the next one but the rest of this (still-scripted) pipeline too.
    const stageLogOverrides: Record<number, string[]> = {
      0: ingestLogs,
      1: [
        `${settings.chunkStrategy} chunker init…`,
        'Splitting documents…',
        `${itemCount} docs → ${chunkCount.toLocaleString()} chunks`,
      ],
      2: [
        `${settings.embedProvider} embed API ready (${embedModel.name})`,
        `Embedding ${chunkCount.toLocaleString()} chunks…`,
        'Done',
      ],
      3: [
        `${settings.vectorStore} collection created`,
        'Inserting vectors…',
        `${chunkCount.toLocaleString()} persisted`,
      ],
      6: [
        `${settings.llmProvider} API connected (${LLM_MODELS[settings.llmProvider]})`,
        'Self-RAG strategy loaded',
        'Generator ready',
      ],
    }
    const stageStatOverrides: Record<number, string> = {
      0: sourceLabel,
      1: `${chunkCount.toLocaleString()} chunks · avg ${avgChunkTokens} tok`,
      2: `dim=${embedModel.dim} · ${settings.embedProvider}`,
      3: `${settings.vectorStore} · ${chunkCount.toLocaleString()} vectors`,
      6: `${LLM_MODELS[settings.llmProvider]} · Self-RAG`,
    }
    setStageStats(stageStatOverrides)

    const failAt = Math.random() < FAILURE_RATE
      ? Math.floor(Math.random() * STAGES.length)
      : -1

    for (let i = 0; i < STAGES.length; i++) {
      if (cancelRef.current) return
      setActiveStage(i)
      const stageLogs = stageLogOverrides[i] ?? STAGES[i].logs.map(l => l.replace(/247/g, String(itemCount)))
      for (const log of stageLogs) {
        if (cancelRef.current) return
        await sleep(300)
        addLog(log)
      }
      await sleep(200)

      if (i === failAt) {
        const errorText = STAGES[i].error.replace(/247/g, String(itemCount))
        addLog(`Stage ${i} (${STAGES[i].name}) failed: ${errorText}`, 'error')
        setFailedStage(i)
        return
      }

      setStagesDone(i + 1)
      await sleep(150)
    }

    await sleep(300)
    addLog('Pipeline complete. Perry the Platypus has not been detected.', 'success')
    setCorpusStats(newCorpusStats)
    await sleep(700)
    setAppState('chat')
  }, [addLog])

  const handleRetry = useCallback(() => {
    const { files, urls } = lastRunRef.current
    runPipeline(files, urls)
  }, [runPipeline])

  const handleReset = () => {
    cancelRef.current = true
    setAppState('drop')
    setStagesDone(0)
    setActiveStage(-1)
    setFailedStage(null)
    setLogs([])
    setStageStats({})
    setCorpusStats(null)
  }

  const statusLabel = appState === 'process'
    ? (failedStage !== null ? 'failed' : 'processing')
    : appState === 'chat' ? 'ready' : 'idle'
  const statusColor = appState === 'drop' ? 'default' : failedStage !== null ? 'error' : 'primary'

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>

        <AppBar position="sticky" elevation={0} color="transparent">
          <Toolbar variant="dense" sx={{ gap: 1 }}>
            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: 'primary.main', mr: 1 }} />
            <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 600, letterSpacing: '-0.02em' }}>
              Raginator
            </Typography>
            <Chip
              label={`${settings.embedProvider} · ${settings.vectorStore}`}
              size="small" variant="outlined"
              onClick={() => setSettingsOpen(true)}
              sx={{ fontFamily: '"JetBrains Mono",monospace', fontSize: '0.68rem', cursor: 'pointer' }}
            />
            <Chip
              label={statusLabel}
              size="small"
              color={statusColor}
              variant={appState === 'drop' ? 'outlined' : 'filled'}
              icon={appState === 'process' && failedStage === null ? <CircularProgress size={10} color="inherit" /> : undefined}
            />
            <IconButton
              size="small"
              onClick={() => setMode(m => (m === 'dark' ? 'light' : 'dark'))}
              aria-label="Toggle dark/light mode"
            >
              {mode === 'dark' ? <LightModeIcon sx={{ fontSize: 18 }} /> : <DarkModeIcon sx={{ fontSize: 18 }} />}
            </IconButton>
          </Toolbar>
        </AppBar>

        {appState === 'drop' && (
          <DropState onStart={runPipeline} settings={settings} onOpenSettings={() => setSettingsOpen(true)} />
        )}

        {appState === 'process' && (
          <ProcessState
            stagesDone={stagesDone}
            activeStage={activeStage}
            failedStage={failedStage}
            stageStats={stageStats}
            logs={logs}
            onRetry={handleRetry}
            onReset={handleReset}
          />
        )}

        {appState === 'chat' && (
          <ChatState
            corpusName={corpusName}
            stats={corpusStats ?? FALLBACK_CORPUS_STATS}
            onReset={handleReset}
          />
        )}

      </Box>

      <SettingsDrawer
        open={settingsOpen}
        settings={settings}
        onChange={setSettings}
        onClose={() => setSettingsOpen(false)}
      />
    </ThemeProvider>
  )
}
