// Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
// SPDX-License-Identifier: Apache-2.0

import React, { useEffect, useRef, useState } from 'react'
import {
  Box, Button, Card, Chip, CircularProgress,
  Dialog, DialogActions, DialogContent, DialogTitle,
  Grid, IconButton, Paper, Stack, TextField, Tooltip, Typography,
} from '@mui/material'
import SendIcon from '@mui/icons-material/Send'
import ManageSearchIcon from '@mui/icons-material/ManageSearch'
import ContentCopyIcon from '@mui/icons-material/ContentCopy'
import CheckIcon from '@mui/icons-material/Check'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import CloseIcon from '@mui/icons-material/Close'
import HistoryIcon from '@mui/icons-material/History'
import { DEMO_QA, EMBED_MODELS, formatBytes, type CorpusStats, type Message, type Provider, type SourceChunk } from '../data'
import { providerIcon } from './icons/ProviderIcons'

interface Props {
  corpusName: string
  stats: CorpusStats
  suggestedQuestions: string[]
  messages: Message[]
  scrollTarget: { index: number; nonce: number } | null
  historyOpen: boolean
  onToggleHistory: () => void
  onSend: (text: string) => Promise<void>
  onReset: () => void
}

// `embeddingModel` is a free-form string like "nomic-embed-text · 768-dim"
// (built server-side from the same EMBED_MODELS table) -- match its model
// name back to a provider so the stat can show that provider's icon.
const providerOfModel = (embeddingModel: string): Provider | undefined =>
  (Object.keys(EMBED_MODELS) as Provider[]).find(p => embeddingModel.includes(EMBED_MODELS[p].name))

const STAT_ITEMS = (stats: CorpusStats) => [
  { label: 'Documents',       value: String(stats.docs), icon: undefined },
  { label: 'Chunks',          value: stats.chunks.toLocaleString(), icon: undefined },
  { label: 'Avg chunk size',  value: `${stats.avgChunkTokens} tok`, icon: undefined },
  { label: 'Embedding model', value: stats.embeddingModel, icon: providerIcon(providerOfModel(stats.embeddingModel) ?? '', 15) },
  { label: 'Index size',      value: formatBytes(stats.indexSizeBytes), icon: undefined },
]

const corpusBarChips = (corpusName: string, stats: CorpusStats) => [
  { label: `◎ ${corpusName}`, color: 'primary' as const },
  { label: `${stats.chunks.toLocaleString()} chunks`, color: 'default' as const },
  { label: `${stats.docs} doc${stats.docs === 1 ? '' : 's'}`, color: 'default' as const },
]

const IS_MAC = typeof navigator !== 'undefined' && /Mac|iPhone|iPad/.test(navigator.platform)

export default function ChatState({
  corpusName, stats, suggestedQuestions, messages, scrollTarget, historyOpen, onToggleHistory, onSend, onReset,
}: Props) {
  const [query, setQuery]       = useState('')
  const [thinking, setThinking] = useState(false)
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null)
  const [previewSource, setPreviewSource] = useState<SourceChunk | null>(null)
  const [inputFocused, setInputFocused] = useState(false)
  const [highlightRange, setHighlightRange] = useState<[number, number] | null>(null)
  const chatRef = useRef<HTMLDivElement>(null)
  const queryInputRef = useRef<HTMLInputElement>(null)
  const messageRefs = useRef<(HTMLDivElement | null)[]>([])

  const copyMessage = (text: string, index: number) => {
    navigator.clipboard.writeText(text)
    setCopiedIndex(index)
    setTimeout(() => setCopiedIndex(null), 1500)
  }

  useEffect(() => {
    if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight
  }, [messages, thinking])

  // Restoring a query from history shows the whole conversation it belongs
  // to (see App.tsx) -- this scrolls to where that specific exchange starts
  // within it and briefly highlights it, overriding the scroll-to-bottom
  // effect above (declared first, so this one wins). Keyed on `nonce`, not
  // just `index`, so clicking the same history entry twice still re-scrolls.
  useEffect(() => {
    if (!scrollTarget) return
    messageRefs.current[scrollTarget.index]?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    setHighlightRange([scrollTarget.index, scrollTarget.index + 1])
    const timer = setTimeout(() => setHighlightRange(null), 1800)
    return () => clearTimeout(timer)
  }, [scrollTarget?.nonce])

  // Cmd/Ctrl+K focuses the query box from anywhere on the page.
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        queryInputRef.current?.focus()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  const sendMessage = async (q?: string) => {
    const text = (q ?? query).trim()
    if (!text || thinking) return
    setQuery('')
    setThinking(true)
    await onSend(text)
    setThinking(false)
  }

  // Real, corpus-derived suggestions from the pipeline's "complete" event
  // when available; otherwise fall back to the canned demo prompts.
  const hasRealSuggestions = suggestedQuestions.length > 0
  const questionChips = hasRealSuggestions ? suggestedQuestions : DEMO_QA.map(qa => qa.q)

  return (
      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 2 }}>

      {/* Corpus bar */}
      <Box sx={{ px: 2, py: 0.75, borderBottom: '0.5px solid rgba(255,255,255,0.08)', bgcolor: 'background.paper', display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
        <Tooltip title={historyOpen ? 'Hide history' : 'Show history'}>
          <IconButton size="small" onClick={onToggleHistory} color={historyOpen ? 'primary' : 'default'}>
            <HistoryIcon sx={{ fontSize: 18 }} />
          </IconButton>
        </Tooltip>
        {corpusBarChips(corpusName, stats).map((c, i) => (
          <Chip key={i} label={c.label} size="small" color={c.color} variant="outlined" />
        ))}
        <Box sx={{ flex: 1 }} />
        <Chip
          icon={<CheckCircleIcon sx={{ fontSize: 14 }} />}
          label="Corpus ready"
          size="small" color="primary" variant="outlined"
        />
        <Button size="small" color="error" variant="outlined" onClick={onReset} sx={{ minWidth: 0, px: 1.5 }}>
          Reset
        </Button>
      </Box>

      {/* Messages */}
      <Box ref={chatRef} sx={{ flex: 1, minHeight: 0, overflowY: 'auto', p: 3, display: 'flex', flexDirection: 'column', gap: 2.5 }}>

        {/* Corpus stats card -- confirms the pipeline actually produced something.
            "Corpus ready" now lives in the bar above, next to Reset. */}
        <Card sx={{ p: 2.5 }}>
          <Grid container spacing={2}>
            {STAT_ITEMS(stats).map(({ label, value, icon }) => (
              <Grid item xs={6} sm={4} md={2.4} key={label}>
                <Typography
                  variant="caption" color="text.secondary"
                  sx={{ fontFamily: '"JetBrains Mono",monospace', fontSize: '0.68rem', display: 'block' }}
                >
                  {label}
                </Typography>
                <Stack direction="row" alignItems="center" spacing={0.5} sx={{ mt: 0.25 }}>
                  {icon}
                  <Typography variant="body2" fontWeight={600}>
                    {value}
                  </Typography>
                </Stack>
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
            ref={(el: HTMLDivElement | null) => { messageRefs.current[i] = el }}
            sx={{ display: 'flex', flexDirection: 'column', alignItems: m.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '78%', alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start' }}
          >
            <Paper
              sx={{
                px: 2, py: 1.5,
                bgcolor: m.role === 'user' ? 'primary.main' : 'background.paper',
                borderRadius: m.role === 'user' ? '12px 12px 3px 12px' : '12px 12px 12px 3px',
                border: m.role === 'user' ? 'none' : '0.5px solid rgba(255,255,255,0.1)',
                boxShadow: highlightRange && i >= highlightRange[0] && i <= highlightRange[1]
                  ? '0 0 0 2px rgba(29,158,117,0.7)' : 'none',
                transition: 'box-shadow 0.4s ease',
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
                    label={s.path.split('/').pop()}
                    size="small"
                    variant="outlined"
                    onClick={() => setPreviewSource(s)}
                    sx={{
                      bgcolor: 'rgba(127,119,221,0.12)', borderColor: 'rgba(127,119,221,0.3)',
                      // #AFA9EC (light lavender) reads fine on dark paper but
                      // is too washed-out on light mode's near-white paper --
                      // swap to a darker purple there for actual contrast.
                      color: theme => (theme.palette.mode === 'dark' ? '#AFA9EC' : '#4F46C2'),
                      fontSize: '0.67rem', height: 20, cursor: 'pointer',
                      '&:hover': { bgcolor: 'rgba(127,119,221,0.22)' },
                    }}
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
          <Stack spacing={0.75} mb={1.5}>
            <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.7rem' }}>
              {hasRealSuggestions ? 'Based on your docs, you might ask…' : 'Try asking…'}
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap">
              {questionChips.map((q, i) => (
                <Chip
                  key={i} label={q} size="small" variant="outlined"
                  onClick={() => sendMessage(q)}
                  sx={{ cursor: 'pointer', fontSize: '0.72rem', '&:hover': { bgcolor: 'rgba(29,158,117,0.1)', borderColor: 'rgba(29,158,117,0.4)', color: 'primary.main' } }}
                />
              ))}
            </Stack>
          </Stack>
        )}

        <Stack direction="row" spacing={1} alignItems="flex-end">
          <TextField
            fullWidth multiline maxRows={4} size="small"
            placeholder="Ask a question about your documents…"
            value={query}
            onChange={e => setQuery(e.target.value)}
            onFocus={() => setInputFocused(true)}
            onBlur={() => setInputFocused(false)}
            onKeyDown={e => {
              if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() }
              else if (e.key === 'Escape') { setQuery('') }
            }}
            inputRef={queryInputRef}
            InputProps={{
              endAdornment: !inputFocused && !query && (
                <Chip
                  label={IS_MAC ? '⌘K' : 'Ctrl K'}
                  size="small" variant="outlined"
                  sx={{ fontSize: '0.65rem', height: 20, color: 'text.secondary', pointerEvents: 'none' }}
                />
              ),
            }}
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

      {/* Source chunk preview -- what was actually retrieved, for debugging RAG quality */}
      <Dialog open={!!previewSource} onClose={() => setPreviewSource(null)} maxWidth="sm" fullWidth>
        {previewSource && (
          <>
            <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, pr: 6 }}>
              <Typography variant="body2" sx={{ fontFamily: '"JetBrains Mono",monospace', fontWeight: 600, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {previewSource.path}
              </Typography>
              <Chip
                label={`score ${previewSource.score.toFixed(2)}`}
                size="small" variant="outlined" color="primary"
                sx={{ fontSize: '0.68rem' }}
              />
              <IconButton size="small" onClick={() => setPreviewSource(null)} sx={{ position: 'absolute', top: 8, right: 8 }}>
                <CloseIcon sx={{ fontSize: 18 }} />
              </IconButton>
            </DialogTitle>
            <DialogContent dividers>
              <Typography
                variant="body2"
                sx={{
                  fontFamily: '"JetBrains Mono",monospace', fontSize: '0.8rem', lineHeight: 1.8,
                  whiteSpace: 'pre-wrap', color: 'text.primary',
                }}
              >
                {previewSource.text}
              </Typography>
            </DialogContent>
            <DialogActions>
              <Button
                size="small" startIcon={<ContentCopyIcon sx={{ fontSize: 14 }} />}
                onClick={() => navigator.clipboard.writeText(previewSource.text)}
              >
                Copy chunk
              </Button>
              <Button size="small" onClick={() => setPreviewSource(null)}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      </Box>
  )
}
