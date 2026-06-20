import React, { useRef, useState } from 'react'
import {
  Box, Button, Chip, Container, IconButton,
  Paper, Stack, TextField, Typography,
} from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import CloseIcon from '@mui/icons-material/Close'
import LinkIcon from '@mui/icons-material/Link'
import DescriptionIcon from '@mui/icons-material/Description'
import ArticleIcon from '@mui/icons-material/Article'
import { formatBytes, STAGES, type PipelineSettings } from '../data'
import { providerIcon } from './icons/ProviderIcons'

interface Props {
  onStart: (files: File[], urls: string[]) => void
  settings: PipelineSettings
  onOpenSettings: () => void
}

const fmtSize = formatBytes

const FileIcon = ({ name }: { name: string }) => {
  if (name.endsWith('.pdf')) return <DescriptionIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
  if (name.endsWith('.md'))  return <ArticleIcon      sx={{ fontSize: 18, color: 'text.secondary' }} />
  return <DescriptionIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
}

// Embed/Generate map to an actual provider brand icon; Store/Chunk don't.
const providerChips = (settings: PipelineSettings) => [
  { label: `Embed: ${settings.embedProvider}`,  color: 'primary'   as const, icon: providerIcon(settings.embedProvider, 14) },
  { label: `Store: ${settings.vectorStore}`,    color: 'secondary' as const, icon: undefined },
  { label: `Chunk: ${settings.chunkStrategy}`,  color: 'default'   as const, icon: undefined },
  { label: `Generate: ${settings.llmProvider}`, color: 'primary'   as const, icon: providerIcon(settings.llmProvider, 14) },
]

export default function DropState({ onStart, settings, onOpenSettings }: Props) {
  const [files, setFiles] = useState<File[]>([])
  const [url, setUrl]     = useState('')
  const [urls, setUrls]   = useState<string[]>([])
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const addFiles = (incoming: FileList | null) => {
    if (!incoming) return
    const arr = Array.from(incoming)
    setFiles(prev => [...prev, ...arr.filter(f => !prev.find(p => p.name === f.name))])
  }

  const addUrl = () => {
    const v = url.trim()
    if (!v) return
    setUrls(prev => [...prev, v])
    setUrl('')
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragging(false)
    addFiles(e.dataTransfer.files)
  }

  const handleStart = () => {
    if (!files.length && !urls.length) return
    onStart(files, urls)
  }

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      <Stack spacing={3} alignItems="center">

        {/* Hero */}
        <Box textAlign="center">
          <Typography variant="overline" color="primary">
            {STAGES.map(s => s.name).join(' → ')}
          </Typography>
          <Typography variant="h4" sx={{ mt: 0.5, mb: 1 }}>
            The RAG-inator
          </Typography>
          <Typography color="text.secondary">
            Drop files or paste a URL. It shall RAG-ify everything.
          </Typography>
        </Box>

        {/* Drop zone */}
        <Paper
          sx={{
            width: '100%', p: 10, textAlign: 'center', cursor: 'pointer',
            border: dragging
              ? '1.5px dashed #1D9E75'
              : '1.5px dashed rgba(255,255,255,0.15)',
            bgcolor: dragging ? 'rgba(29,158,117,0.06)' : 'background.paper',
            transition: 'all .2s',
            '&:hover': { borderColor: '#1D9E75', bgcolor: 'rgba(29,158,117,0.04)' },
          }}
          onDragOver={e => { e.preventDefault(); setDragging(true) }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
        >
          <input
            ref={inputRef}
            type="file"
            multiple
            accept=".pdf,.txt,.md,.docx"
            style={{ display: 'none' }}
            onChange={e => addFiles(e.target.files)}
          />
          <CloudUploadIcon sx={{ fontSize: 36, opacity: 0.4, mb: 1 }} />
          <Typography variant="body1" fontWeight={500}>Drop files here</Typography>
          <Typography variant="body2" color="text.secondary" mt={0.5}>
            PDF, TXT, MD, DOCX — or click to browse
          </Typography>
        </Paper>

        {/* URL input */}
        <Stack direction="row" spacing={1} width="100%">
          <TextField
            fullWidth size="small"
            placeholder="https://docs.mistral.ai  or  github.com/owner/repo"
            value={url}
            onChange={e => setUrl(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && addUrl()}
          />
          <Button variant="outlined" onClick={addUrl} sx={{ whiteSpace: 'nowrap' }}>
            Add URL
          </Button>
        </Stack>

        {/* File list */}
        {(files.length > 0 || urls.length > 0) && (
          <Stack spacing={0.75} width="100%">
            {files.map((f, i) => (
              <Paper key={'f' + i} sx={{ px: 2, py: 1, display: 'flex', alignItems: 'center', gap: 1.5 }}>
                <FileIcon name={f.name} />
                <Typography variant="body2" sx={{ flex: 1, fontFamily: '"JetBrains Mono",monospace', fontSize: '0.75rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {f.name}
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ fontFamily: '"JetBrains Mono",monospace' }}>
                  {fmtSize(f.size)}
                </Typography>
                <IconButton size="small" onClick={() => setFiles(f => f.filter((_, j) => j !== i))}>
                  <CloseIcon sx={{ fontSize: 16 }} />
                </IconButton>
              </Paper>
            ))}
            {urls.map((u, i) => (
              <Paper key={'u' + i} sx={{ px: 2, py: 1, display: 'flex', alignItems: 'center', gap: 1.5 }}>
                <LinkIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
                <Typography variant="body2" sx={{ flex: 1, fontFamily: '"JetBrains Mono",monospace', fontSize: '0.75rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {u}
                </Typography>
                <IconButton size="small" onClick={() => setUrls(u => u.filter((_, j) => j !== i))}>
                  <CloseIcon sx={{ fontSize: 16 }} />
                </IconButton>
              </Paper>
            ))}
          </Stack>
        )}

        {/* Provider chips -- click any of them to open pipeline settings */}
        <Stack direction="row" spacing={1} flexWrap="wrap" justifyContent="center">
          {providerChips(settings).map(({ label, color, icon }, i) => (
            <Chip
              key={i} label={label} size="small" color={color} variant="outlined"
              icon={icon}
              onClick={onOpenSettings}
              sx={{ cursor: 'pointer' }}
            />
          ))}
        </Stack>

        {/* CTA -- gradient picks up the same primary->secondary two-tone as
            the "RAG FACTORY" title in the AppBar, instead of a flat fill. */}
        <Button
          variant="contained" color="primary" fullWidth size="large"
          endIcon={<span style={{ fontSize: 20 }}>›</span>}
          onClick={handleStart}
          disabled={!files.length && !urls.length}
          sx={{
            py: 1.5, fontSize: '0.95rem',
            background: 'linear-gradient(135deg, #1D9E75 0%, #7F77DD 100%)',
            boxShadow: '0 4px 14px rgba(29,158,117,0.35)',
            transition: 'all .25s',
            '&:hover': {
              background: 'linear-gradient(135deg, #1bb084 0%, #8f88ea 100%)',
              boxShadow: '0 6px 18px rgba(127,119,221,0.4)',
            },
            // MUI's default disabled tokens (action.disabled/disabledBackground)
            // are deliberately low-opacity gray-on-gray -- low contrast by
            // Material convention, but it reads as barely-there here. Use a
            // clearly bordered, clearly legible gray instead.
            '&.Mui-disabled': {
              background: 'none',
              bgcolor: theme => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.06)',
              color: theme => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.6)' : 'rgba(0,0,0,0.55)',
              border: '1px solid',
              borderColor: theme => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.18)' : 'rgba(0,0,0,0.18)',
              boxShadow: 'none',
            },
          }}
        >
          Start Raginator
        </Button>

      </Stack>
    </Container>
  )
}
