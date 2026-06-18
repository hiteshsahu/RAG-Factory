import React, { useEffect, useRef, useState } from 'react'
import {
  Box, Button, Card, Chip, CircularProgress,
  Grid, IconButton, Paper, Stack, TextField, Tooltip, Typography,
} from '@mui/material'
import SendIcon from '@mui/icons-material/Send'
import ManageSearchIcon from '@mui/icons-material/ManageSearch'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import CheckIcon from '@mui/icons-material/Check'
import { DEMO_QA, DemoAnswer, formatBytes, type CorpusStats } from '../data'

interface Message {
  role: 'user' | 'bot'
  text: string
  sources?: string[]
  ms?: number
  tokens?: number
  cost?: string
}

interface Props {
  corpusName: string
  stats: CorpusStats
  onReset: () => void
}

const STAT_ITEMS = (stats: CorpusStats) => [
  { label: 'Documents',       value: String(stats.docs) },
  { label: 'Chunks',          value: stats.chunks.toLocaleString() },
  { label: 'Avg chunk size',  value: `${stats.avgChunkTokens} tok` },
  { label: 'Embedding model', value: stats.embeddingModel },
  { label: 'Index size',      value: formatBytes(stats.indexSizeBytes) },
]

const sleep = (ms: number) => new Promise(r => setTimeout(r, ms))

export default function ChatState({ corpusName, stats, onReset }: Props) {
  const [messages, setMessages] = useState<Message[]>([])
  const [query, setQuery]       = useState('')
  const [thinking, setThinking] = useState(false)
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)
  const chatRef = useRef<HTMLDivElement>(null)

  const copyMessage = (text: string, index: number) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 1500)
  }

  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight
  }, [messages, thinking])

  const sendMessage = async (q?: string) => {
    const text = (q ?? query).trim()
    if (!text || thinking) return
    setQuery('')
    setMessages(m => [...m, { role: 'user', text }])
    setThinking(true)
    await sleep(700 + Math.random() * 500)

    const words = text.toLowerCase().split(' ').slice(0, 3).join(' ')
    const match: DemoAnswer =
      DEMO_QA.find(a => a.q.toLowerCase().includes(words)) ??
      DEMO_QA[Math.floor(Math.random() * DEMO_QA.length)]

    setThinking(false)
    setMessages(m => [...m, { role: 'bot', text: match.a, sources: match.sources, ms: match.ms, tokens: match.tokens, cost: match.cost }])
  }

  return (
    <Box sx={{
      display: 'flex',
      flexDirection: 'column',
      height: 'calc(100vh - 48px)',
      p: 2}}>

      {/* Corpus bar */}
      <Box sx={{ px: 2, py: 0.75, borderBottom: '0.5px solid rgba(255,255,255,0.08)', bgcolor: 'background.paper', display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
        <Chip label={`◎ ${corpusName}`} size="small" color="primary" variant="outlined" />
        <Chip label={`${stats.chunks.toLocaleString()} chunks`} size="small" variant="outlined" />
        <Chip label={`${stats.docs} doc${stats.docs === 1 ? '' : 's'}`} size="small" variant="outlined" />
        <Box sx={{ flex: 1 }} />
        <Button size="small" color="error" variant="outlined" onClick={onReset} sx={{ minWidth: 0, px: 1.5 }}>
          Reset
        </Button>
      </Box>

      {/* Messages */}
      <Box ref={chatRef} sx={{ flex: 1, overflowY: 'auto', p: 3, display: 'flex', flexDirection: 'column', gap: 2.5 }}>

        {/* Corpus stats card -- confirms the pipeline actually produced something */}
        <Card sx={{ p: 2.5 }}>
          <Typography variant="overline" color="primary">✓ Corpus ready</Typography>
          <Grid container spacing={2} mt={1}>
            {STAT_ITEMS(stats).map(({ label, value }) => (
              <Grid item xs={6} sm={4} md={2.4} key={label}>
                <Typography
                  variant="caption" color="text.secondary"
                  sx={{ fontFamily: '"JetBrains Mono",monospace', fontSize: '0.68rem', display: 'block' }}
                >
                  {label}
                </Typography>
                <Typography variant="body2" fontWeight={600} sx={{ mt: 0.25 }}>
                  {value}
                </Typography>
              </Grid>
            ))}
          </Grid>
        </Card>

        {messages.length === 0 && !thinking && (
          <Stack alignItems="center" justifyContent="center" sx={{ flex: 1, opacity: 0.4, py: 6 }} spacing={1}>
            <ManageSearchIcon sx={{ fontSize: 36 }} />
            <Typography color="text.secondary" fontSize="0.875rem">Corpus ready. Ask anything.</Typography>
          </Stack>
        )}

        {messages.map((m, i) => (
          <Box
            key={i}
            sx={{ display: 'flex', flexDirection: 'column', alignItems: m.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '78%', alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start' }}
          >
            <Paper
              sx={{
                px: 2, py: 1.5,
                bgcolor: m.role === 'user' ? 'primary.main' : 'background.paper',
                borderRadius: m.role === 'user' ? '12px 12px 3px 12px' : '12px 12px 12px 3px',
                border: m.role === 'user' ? 'none' : '0.5px solid rgba(255,255,255,0.1)',
                position: 'relative',
                '&:hover .copy-btn': { opacity: 1 },
              }}
            >
              <Typography variant="body2" sx={{ color: m.role === 'user' ? '#fff' : 'text.primary', lineHeight: 1.7 }}>
                {m.text}
              </Typography>

              {m.role === 'bot' && (
                <Tooltip title={copiedIndex === i ? 'Copied!' : 'Copy answer'}>
                  <IconButton
                    className="copy-btn"
                    size="small"
                    onClick={() => copyMessage(m.text, i)}
                    sx={{ position: 'absolute', top: 4, right: 4, opacity: 0, transition: 'opacity .15s', color: 'text.secondary' }}
                  >
                    {copiedIndex === i ? <CheckIcon sx={{ fontSize: 14, color: 'primary.main' }} /> : <ContentCopyIcon sx={{ fontSize: 14 }} />}
                  </IconButton>
                </Tooltip>
              )}
            </Paper>

            {m.role === 'bot' && m.sources && (
              <Stack direction="row" spacing={0.5} mt={0.75} flexWrap="wrap">
                {m.sources.map((s, j) => (
                  <Chip
                    key={j}
                    label={s.split('/').pop()}
                    size="small"
                    variant="outlined"
                    sx={{ bgcolor: 'rgba(127,119,221,0.12)', color: '#AFA9EC', borderColor: 'rgba(127,119,221,0.3)', fontSize: '0.67rem', height: 20 }}
                  />
                ))}
              </Stack>
            )}

            {m.role === 'bot' && m.ms && (
              <Stack direction="row" spacing={1.5} mt={0.5} px={0.5}>
                {[`${m.ms}ms`, `${m.tokens} tok`, m.cost].map((v, j) => (
                  <Typography key={j} variant="caption" sx={{ fontFamily: '"JetBrains Mono",monospace', color: 'text.secondary', fontSize: '0.68rem' }}>
                    {v}
                  </Typography>
                ))}
              </Stack>
            )}
          </Box>
        ))}

        {thinking && (
          <Paper sx={{ px: 2, py: 1.5, display: 'inline-flex', alignItems: 'center', gap: 1, borderRadius: '12px 12px 12px 3px', border: '0.5px solid rgba(255,255,255,0.1)', alignSelf: 'flex-start' }}>
            <CircularProgress size={12} color="primary" />
            <Typography variant="caption" color="text.secondary">Retrieving…</Typography>
          </Paper>
        )}
      </Box>

      {/* Input area */}
      <Box sx={{ p: 2, borderTop: '0.5px solid rgba(255,255,255,0.08)', bgcolor: 'background.default' }}>
        {messages.length === 0 && (
          <Stack direction="row" spacing={1} mb={1.5} flexWrap="wrap">
            {DEMO_QA.map((qa, i) => (
              <Chip
                key={i} label={qa.q} size="small" variant="outlined"
                onClick={() => sendMessage(qa.q)}
                sx={{ cursor: 'pointer', fontSize: '0.72rem', '&:hover': { bgcolor: 'rgba(29,158,117,0.1)', borderColor: 'rgba(29,158,117,0.4)', color: 'primary.main' } }}
              />
            ))}
          </Stack>
        )}

        <Stack direction="row" spacing={1} alignItems="flex-end">
          <TextField
            fullWidth multiline maxRows={4} size="small"
            placeholder="Ask a question about your documents…"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() } }}
          />
          <IconButton
            color="primary"
            onClick={() => sendMessage()}
            disabled={thinking || !query.trim()}
            sx={{ bgcolor: 'primary.main', color: '#fff', width: 40, height: 40, borderRadius: 1.5, '&:hover': { bgcolor: '#18b887' }, '&.Mui-disabled': { bgcolor: 'rgba(29,158,117,0.2)' } }}
          >
            <SendIcon sx={{ fontSize: 18 }} />
          </IconButton>
        </Stack>
      </Box>

    </Box>
  )
}
