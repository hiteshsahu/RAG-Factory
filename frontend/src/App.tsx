import React, { useCallback, useMemo, useRef, useState } from 'react'
import {
  AppBar, Box, Chip, CircularProgress,
  CssBaseline, IconButton, ThemeProvider, Toolbar, Typography,
} from '@mui/material'
import type { PaletteMode } from '@mui/material'
import LightModeIcon from '@mui/icons-material/LightMode'
import DarkModeIcon from '@mui/icons-material/DarkMode'
import getTheme from './theme'
import { DEFAULT_SETTINGS, EMBED_MODELS, type CorpusStats, type Message, type PipelineSettings } from './data'
import { streamPipelineStart, queryBackend } from './apiClient'
import { useLocalStorage } from './hooks/useLocalStorage'
import DropState from './components/DropState'
import ProcessState from './components/ProcessState'
import ChatState from './components/ChatState'
import SettingsDrawer from './components/SettingsDrawer'
import HistoryDrawer, { type HistoryEntry } from './components/HistoryDrawer'

type AppState = 'drop' | 'process' | 'chat'

interface LogLine { text: string; kind: 'default' | 'success' | 'error' }

interface FullHistoryEntry extends HistoryEntry {
  messages: Message[]
}

const sleep = (ms: number) => new Promise(r => setTimeout(r, ms))

// -1 is a sentinel for "failed before any stage started" (preflight, or a
// connection error) -- distinct from `null` (no failure) and from a real
// stage index (0-7).
const PREFLIGHT_STAGE = -1

const FALLBACK_CORPUS_STATS: CorpusStats = {
  docs: 0, chunks: 0, avgChunkTokens: 0,
  embeddingModel: `${EMBED_MODELS.Ollama.name} · ${EMBED_MODELS.Ollama.dim}-dim`,
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
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([])
  const [corpusName, setCorpusName] = useState('')
  const [settings, setSettings] = useLocalStorage<PipelineSettings>('raginator:settings', DEFAULT_SETTINGS)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [history, setHistory] = useLocalStorage<FullHistoryEntry[]>('raginator:chat-history', [])
  const [historyOpen, setHistoryOpen] = useState(false)
  const [activeHistoryId, setActiveHistoryId] = useState<number | null>(null)
  const [mode, setMode] = useState<PaletteMode>('dark')
  const theme = useMemo(() => getTheme(mode), [mode])
  const cancelRef = useRef(false)
  const lastRunRef = useRef<{ files: File[]; urls: string[] }>({ files: [], urls: [] })
  // Resume id numbering above whatever was already persisted, so restored
  // entries from a previous session can't collide with new ones.
  const historyIdRef = useRef(history.reduce((max, h) => Math.max(max, h.id), 0))

  const addLog = useCallback((text: string, kind: LogLine['kind'] = 'default') => {
    setLogs(l => [...l, { text, kind }])
  }, [])

  const runPipeline = useCallback(async (files: File[], urls: string[]) => {
    cancelRef.current = false
    lastRunRef.current = { files, urls }

    setAppState('process')
    setStagesDone(0)
    setActiveStage(0)
    setFailedStage(null)
    setLogs([])
    setStageStats({})
    setCorpusStats(null)
    setSuggestedQuestions([])

    if (files.length === 0) {
      // The bridge only ingests real files -- WebIngestor/GitHubIngestor
      // aren't wired in yet, so a URL-only run can't actually be honored.
      setCorpusName(urls[0] ? new URL(urls[0]).hostname : 'corpus')
      addLog("URL ingestion isn't wired into the bridge yet -- drop a file instead (PDF, TXT, or MD).", 'error')
      setFailedStage(PREFLIGHT_STAGE)
      return
    }
    setCorpusName(files[0].name.replace(/\.[^.]+$/, ''))

    try {
      for await (const event of streamPipelineStart(files, settings)) {
        if (cancelRef.current) return

        switch (event.type) {
          case 'preflight_failed':
            for (const err of event.errors ?? []) addLog(err, 'error')
            setFailedStage(PREFLIGHT_STAGE)
            return

          case 'log':
            if (event.stage !== undefined) setActiveStage(event.stage)
            addLog(event.text ?? '', event.kind ?? 'default')
            break

          case 'stage_done':
            if (event.stage !== undefined) {
              setStagesDone(event.stage + 1)
              if (event.stat) {
                const stage = event.stage
                const stat = event.stat
                setStageStats(s => ({ ...s, [stage]: stat }))
              }
            }
            break

          case 'error':
            addLog(event.text ?? 'Unknown error', 'error')
            setFailedStage(event.stage ?? PREFLIGHT_STAGE)
            return

          case 'complete':
            addLog('Pipeline complete.', 'success')
            if (event.corpusStats) setCorpusStats(event.corpusStats)
            if (event.suggestedQuestions) setSuggestedQuestions(event.suggestedQuestions)
            await sleep(500)
            setAppState('chat')
            return
        }
      }
    } catch (err) {
      addLog(err instanceof Error ? err.message : String(err), 'error')
      setFailedStage(PREFLIGHT_STAGE)
    }
  }, [addLog, settings])

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
    setSuggestedQuestions([])
    setMessages([])
    setActiveHistoryId(null)
  }

  // Lives at the App level (not ChatState) so the history drawer's persistent
  // icon rail stays meaningful across all three app states, not just chat.
  const sendMessage = useCallback(async (text: string) => {
    const userMsg: Message = { role: 'user', text }
    setMessages(m => [...m, userMsg])
    setActiveHistoryId(null)

    let botMsg: Message
    try {
      const result = await queryBackend(text)
      botMsg = {
        role: 'bot', text: result.answer, sources: result.sources,
        ms: result.ms, tokens: result.tokens, cost: result.cost,
      }
    } catch (err) {
      botMsg = { role: 'bot', text: `⚠️ ${err instanceof Error ? err.message : String(err)}` }
    }

    setMessages(m => [...m, botMsg])
    const id = ++historyIdRef.current
    setHistory(h => [{ id, query: text, time: Date.now(), messages: [userMsg, botMsg] }, ...h])
    setActiveHistoryId(id)
  }, [setHistory])

  const restoreHistoryEntry = useCallback((entry: HistoryEntry) => {
    const full = history.find(h => h.id === entry.id)
    if (!full) return
    setMessages(full.messages)
    setActiveHistoryId(full.id)
    setHistoryOpen(false)
    // History is global (visible from drop/process too) but a restored
    // conversation only makes sense in the chat view -- jump there.
    setAppState('chat')
  }, [history])

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
            <Typography
              variant="h6"
              onClick={handleReset}
              sx={{
                flexGrow: 1, fontWeight: 600, letterSpacing: '-0.02em', cursor: 'pointer',
                userSelect: 'none', '&:hover': { opacity: 0.8 },
              }}
            >
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

        <Box sx={{ display: 'flex', minHeight: 'calc(100vh - 48px)' }}>
          <HistoryDrawer
            open={historyOpen}
            entries={history}
            activeId={activeHistoryId}
            onSelect={restoreHistoryEntry}
            onClose={() => setHistoryOpen(false)}
            onOpen={() => setHistoryOpen(true)}
          />

          <Box sx={{ flex: 1, minWidth: 0 }}>
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
                suggestedQuestions={suggestedQuestions}
                messages={messages}
                historyOpen={historyOpen}
                onToggleHistory={() => setHistoryOpen(o => !o)}
                onSend={sendMessage}
                onReset={handleReset}
              />
            )}
          </Box>

          <SettingsDrawer
            open={settingsOpen}
            settings={settings}
            onChange={setSettings}
            onClose={() => setSettingsOpen(false)}
            onOpen={() => setSettingsOpen(true)}
          />
        </Box>

      </Box>
    </ThemeProvider>
  )
}
