import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
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
import HistoryDrawer, { type CorpusHistory, type SourceType } from './components/HistoryDrawer'
import { PROVIDER_ICON } from './components/icons/ProviderIcons'

type AppState = 'drop' | 'process' | 'chat'

interface LogLine { text: string; kind: 'default' | 'success' | 'error' }

const sourceTypeOf = (files: File[], urls: string[]): SourceType => {
  if (files.length > 0) return files[0].name.toLowerCase().endsWith('.pdf') ? 'pdf' : 'doc'
  return urls.length > 0 ? 'url' : 'doc'
}

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
  // Off by default behavior is "jump straight to chat" -- this just lets
  // that be paused so the final stage tiles/log are still on screen to
  // actually look at, instead of vanishing 500ms after the run finishes.
  const [autoAdvance, setAutoAdvance] = useLocalStorage<boolean>('raginator:auto-advance', true)
  const [settings, setSettings] = useLocalStorage<PipelineSettings>('raginator:settings', DEFAULT_SETTINGS)
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  // v3: added per-corpus suggestedQuestions (v2 added the stats snapshot) --
  // bumped key again so entries missing the new field are abandoned rather
  // than loaded with `undefined` suggestions.
  const [corpusHistory, setCorpusHistory] = useLocalStorage<CorpusHistory[]>('raginator:corpus-history-v3', [])
  const [historyOpen, setHistoryOpen] = useState(false)
  const [activeCorpusId, setActiveCorpusId] = useState<string | null>(null)
  const [activeQueryId, setActiveQueryId] = useState<number | null>(null)
  const [scrollTarget, setScrollTarget] = useState<{ index: number; nonce: number } | null>(null)
  const scrollNonceRef = useRef(0)
  const [mode, setMode] = useState<PaletteMode>('dark')
  const theme = useMemo(() => getTheme(mode), [mode])
  const cancelRef = useRef(false)
  const lastRunRef = useRef<{ files: File[]; urls: string[] }>({ files: [], urls: [] })
  // Resume id numbering above whatever was already persisted, so restored
  // entries from a previous session can't collide with new ones.
  const queryIdRef = useRef(
    corpusHistory.reduce((max, c) => c.queries.reduce((m, q) => Math.max(m, q.id), max), 0),
  )
  const corpusIdRef = useRef(corpusHistory.length)
  // True once the real 'complete' event has landed (corpusStats/suggestions/
  // history already populated) -- distinct from "all 8 stage tiles are
  // done", since the suggestion-generation LLM call still runs *after* the
  // last stage_done event, before 'complete' actually fires.
  const [pipelineDone, setPipelineDone] = useState(false)

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
    setPipelineDone(false)

    if (files.length === 0) {
      // The bridge only ingests real files -- WebIngestor/GitHubIngestor
      // aren't wired in yet, so a URL-only run can't actually be honored.
      setCorpusName(urls[0] ? new URL(urls[0]).hostname : 'corpus')
      addLog("URL ingestion isn't wired into the bridge yet -- drop a file instead (PDF, TXT, or MD).", 'error')
      setFailedStage(PREFLIGHT_STAGE)
      return
    }
    const name = files[0].name.replace(/\.[^.]+$/, '')
    setCorpusName(name)

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

          case 'complete': {
            addLog('Pipeline complete.', 'success')
            if (event.corpusStats) setCorpusStats(event.corpusStats)
            if (event.suggestedQuestions) setSuggestedQuestions(event.suggestedQuestions)

            // A successful upload starts a new corpus group at the top of
            // history -- every question asked from here on (until the next
            // upload or reset) nests under it.
            const corpusId = `corpus-${++corpusIdRef.current}`
            setActiveCorpusId(corpusId)
            setActiveQueryId(null)
            setCorpusHistory(h => [
              {
                corpusId,
                corpusName: name,
                sourceType: sourceTypeOf(files, urls),
                stats: event.corpusStats ?? FALLBACK_CORPUS_STATS,
                suggestedQuestions: event.suggestedQuestions ?? [],
                createdAt: Date.now(),
                queries: [],
              },
              ...h,
            ])

            // Whether we navigate now or wait for the user is decided by the
            // effect below, which reacts live to `autoAdvance` -- including
            // if it gets toggled on *after* this point, once the run has
            // already finished.
            setPipelineDone(true)
            return
          }
        }
      }
    } catch (err) {
      addLog(err instanceof Error ? err.message : String(err), 'error')
      setFailedStage(PREFLIGHT_STAGE)
    }
  }, [addLog, settings, setCorpusHistory])

  // Drives the process -> chat transition off live state instead of a
  // one-shot check inside runPipeline -- so flipping auto-advance on *after*
  // the pipeline already finished (banner still showing, button skipped)
  // still navigates, instead of silently doing nothing.
  useEffect(() => {
    if (!pipelineDone || !autoAdvance || appState !== 'process') return
    const timer = setTimeout(() => setAppState('chat'), 500)
    return () => clearTimeout(timer)
  }, [pipelineDone, autoAdvance, appState])

  // Manual escape hatch for when auto-advance is off and the pipeline has
  // already finished -- the stage tiles/log stay on screen until this fires.
  const continueToChat = useCallback(() => setAppState('chat'), [])

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
    setPipelineDone(false)
    setMessages([])
    setActiveCorpusId(null)
    setActiveQueryId(null)
  }

  // Lives at the App level (not ChatState) so the history drawer's persistent
  // icon rail stays meaningful across all three app states, not just chat.
  const sendMessage = useCallback(async (text: string) => {
    const userMsg: Message = { role: 'user', text }
    setMessages(m => [...m, userMsg])

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

    const queryId = ++queryIdRef.current
    setCorpusHistory(h => h.map(corpus =>
      corpus.corpusId === activeCorpusId
        ? { ...corpus, queries: [...corpus.queries, { id: queryId, question: text, messages: [userMsg, botMsg], timestamp: Date.now() }] }
        : corpus,
    ))
    setActiveQueryId(queryId)
  }, [activeCorpusId, setCorpusHistory])

  const restoreQuery = useCallback((corpusId: string, queryId: number) => {
    const corpus = corpusHistory.find(c => c.corpusId === corpusId)
    const queryIndex = corpus?.queries.findIndex(q => q.id === queryId) ?? -1
    if (!corpus || queryIndex === -1) return

    // Show the whole conversation for this corpus, not just the one exchange
    // that was clicked -- then scroll to where that exchange starts within
    // it, so the rest of the back-and-forth is still right there to scroll
    // through instead of being thrown away.
    const allMessages = corpus.queries.flatMap(q => q.messages)
    const scrollIndex = corpus.queries.slice(0, queryIndex).reduce((sum, q) => sum + q.messages.length, 0)

    setMessages(allMessages)
    setCorpusName(corpus.corpusName)
    // Real snapshot from when this corpus was indexed -- not necessarily
    // what's actually loaded server-side right now (the bridge only tracks
    // one corpus at a time), but accurate for what this conversation was
    // originally about, which is what the stats card should reflect.
    setCorpusStats(corpus.stats)
    setSuggestedQuestions(corpus.suggestedQuestions)
    setActiveCorpusId(corpusId)
    setActiveQueryId(queryId)
    // History is global (visible from drop/process too) but a restored
    // conversation only makes sense in the chat view -- jump there. The
    // drawer itself stays open -- selecting an item shouldn't close it.
    setAppState('chat')
    setScrollTarget({ index: scrollIndex, nonce: ++scrollNonceRef.current })
  }, [corpusHistory])

  // Clicking a corpus with no queries yet (nothing to restore) still needs
  // to land you in its chat -- just with an empty conversation.
  const selectCorpus = useCallback((corpusId: string) => {
    const corpus = corpusHistory.find(c => c.corpusId === corpusId)
    if (!corpus) return
    setMessages(corpus.queries.flatMap(q => q.messages))
    setCorpusName(corpus.corpusName)
    setCorpusStats(corpus.stats)
    setSuggestedQuestions(corpus.suggestedQuestions)
    setActiveCorpusId(corpusId)
    setActiveQueryId(corpus.queries[corpus.queries.length - 1]?.id ?? null)
    setAppState('chat')
  }, [corpusHistory])

  const statusLabel = appState === 'process'
    ? (failedStage !== null ? 'failed' : 'processing')
    : appState === 'chat' ? 'ready' : 'idle'
  const statusColor = appState === 'drop' ? 'default' : failedStage !== null ? 'error' : 'primary'

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ height: '100vh', overflow: 'hidden', display: 'flex', flexDirection: 'column', bgcolor: 'background.default' }}>

        <AppBar position="static" elevation={0} color="transparent">
          <Toolbar  sx={{ gap: 1 }}>
            <Box
                component="img"
                src="/duck-icon.png"
                alt=""
                aria-hidden
                sx={{ width: 48, height: 48, objectFit: 'contain', mr: 1 }}
            />
            <Typography
              variant="h6"
              onClick={handleReset}
              sx={{
                flexGrow: 1, fontWeight: 600, letterSpacing: '0.02em', cursor: 'pointer',
                userSelect: 'none', '&:hover': { opacity: 0.8 },
              }}
            >
              <Box component="span" sx={{ color: 'primary.main' }}>RAG</Box>
              {' '}
              <Box component="span" sx={{ color: 'secondary.main' }}>FACTORY</Box>
            </Typography>

            <Chip
              icon={React.createElement(PROVIDER_ICON[settings.embedProvider], { sx: { fontSize: 14 } })}
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

        {/* flex:1+minHeight:0 (not a hardcoded "100vh - AppBar height") so this
            always takes exactly whatever's left below the AppBar, regardless
            of its actual rendered height -- the page itself never scrolls;
            only the panes below that declare their own overflow do. */}
        <Box sx={{ display: 'flex', flex: 1, minHeight: 0 }}>
          <HistoryDrawer
            open={historyOpen}
            corpora={corpusHistory}
            activeCorpusId={activeCorpusId}
            activeQueryId={activeQueryId}
            onSelect={restoreQuery}
            onSelectCorpus={selectCorpus}
            onNew={handleReset}
            onClose={() => setHistoryOpen(false)}
            onOpen={() => setHistoryOpen(true)}
          />

          <Box sx={{ flex: 1, minWidth: 0, overflowY: 'auto' }}>
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
                pipelineDone={pipelineDone}
                onRetry={handleRetry}
                onReset={handleReset}
                autoAdvance={autoAdvance}
                onToggleAutoAdvance={() => setAutoAdvance(v => !v)}
                onContinue={continueToChat}
              />
            )}

            {appState === 'chat' && (
              <ChatState
                corpusName={corpusName}
                stats={corpusStats ?? FALLBACK_CORPUS_STATS}
                suggestedQuestions={suggestedQuestions}
                messages={messages}
                scrollTarget={scrollTarget}
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
