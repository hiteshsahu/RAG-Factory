import React, { useCallback, useMemo, useRef, useState } from 'react'
import {
  AppBar, Box, Chip, CircularProgress,
  CssBaseline, IconButton, ThemeProvider, Toolbar, Typography,
} from '@mui/material'
import type { PaletteMode } from '@mui/material'
import LightModeIcon from '@mui/icons-material/LightMode'
import DarkModeIcon from '@mui/icons-material/DarkMode'
import getTheme from './theme'
import { STAGES, formatBytes } from './data'
import DropState from './components/DropState'
import ProcessState from './components/ProcessState'
import ChatState from './components/ChatState'

type AppState = 'drop' | 'process' | 'chat'

interface LogLine { text: string; kind: 'default' | 'success' | 'error' }

const sleep = (ms: number) => new Promise(r => setTimeout(r, ms))

// Demo-only: simulates real pipelines failing partway through, so the UI's
// error handling is actually exercised instead of always happy-pathing.
const FAILURE_RATE = 0.3

export default function App() {
  const [appState, setAppState]     = useState<AppState>('drop')
  const [stagesDone, setStagesDone] = useState(0)
  const [activeStage, setActiveStage] = useState(-1)
  const [failedStage, setFailedStage] = useState<number | null>(null)
  const [logs, setLogs]             = useState<LogLine[]>([])
  const [stageStats, setStageStats] = useState<Record<number, string>>({})
  const [corpusName, setCorpusName] = useState('')
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
    setStageStats({ 0: sourceLabel })

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

    const failAt = Math.random() < FAILURE_RATE
      ? Math.floor(Math.random() * STAGES.length)
      : -1

    for (let i = 0; i < STAGES.length; i++) {
      if (cancelRef.current) return
      setActiveStage(i)
      const stageLogs = i === 0 ? ingestLogs : STAGES[i].logs.map(l => l.replace(/247/g, String(itemCount)))
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
              label="Mistral · ChromaDB"
              size="small" variant="outlined"
              sx={{ fontFamily: '"JetBrains Mono",monospace', fontSize: '0.68rem' }}
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
          <DropState onStart={runPipeline} />
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
            onReset={handleReset}
          />
        )}

      </Box>
    </ThemeProvider>
  )
}
