import React, { useCallback, useRef, useState } from 'react'
import {
  AppBar, Box, Chip, CircularProgress,
  CssBaseline, ThemeProvider, Toolbar, Typography,
} from '@mui/material'
import theme from './theme'
import { STAGES } from './data'
import DropState from './components/DropState'
import ProcessState from './components/ProcessState'
import ChatState from './components/ChatState'

type AppState = 'drop' | 'process' | 'chat'

interface LogLine { text: string; ok: boolean }

const sleep = (ms: number) => new Promise(r => setTimeout(r, ms))

export default function App() {
  const [appState, setAppState]     = useState<AppState>('drop')
  const [stagesDone, setStagesDone] = useState(0)
  const [activeStage, setActiveStage] = useState(-1)
  const [logs, setLogs]             = useState<LogLine[]>([])
  const [corpusName, setCorpusName] = useState('')
  const cancelRef = useRef(false)

  const addLog = useCallback((text: string, ok = false) => {
    setLogs(l => [...l, { text, ok }])
  }, [])

  const runPipeline = useCallback(async (files: File[], urls: string[]) => {
    cancelRef.current = false
    const name = files.length
      ? files[0].name.replace(/\.[^.]+$/, '')
      : new URL(urls[0]).hostname
    setCorpusName(name)
    setAppState('process')
    setStagesDone(0)
    setActiveStage(0)
    setLogs([])

    for (let i = 0; i < STAGES.length; i++) {
      if (cancelRef.current) return
      setActiveStage(i)
      for (const log of STAGES[i].logs) {
        if (cancelRef.current) return
        await sleep(300)
        addLog(log)
      }
      await sleep(200)
      setStagesDone(i + 1)
      await sleep(150)
    }

    await sleep(300)
    addLog('Pipeline complete. Perry the Platypus has not been detected.', true)
    await sleep(700)
    setAppState('chat')
  }, [addLog])

  const handleReset = () => {
    cancelRef.current = true
    setAppState('drop')
    setStagesDone(0)
    setActiveStage(-1)
    setLogs([])
  }

  const statusLabel = appState === 'process' ? 'processing' : appState === 'chat' ? 'ready' : 'idle'
  const statusColor = appState === 'drop' ? 'default' : 'primary'

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
              icon={appState === 'process' ? <CircularProgress size={10} color="inherit" /> : undefined}
            />
          </Toolbar>
        </AppBar>

        {appState === 'drop' && (
          <DropState onStart={runPipeline} />
        )}

        {appState === 'process' && (
          <ProcessState
            stagesDone={stagesDone}
            activeStage={activeStage}
            logs={logs}
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
