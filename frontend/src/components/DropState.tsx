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

interface Props {
  onStart: (files: File[], urls: string[]) => void
}

const fmtSize = (b: number) =>
  b > 1_048_576 ? (b / 1_048_576).toFixed(1) + ' MB' : Math.round(b / 1024) + ' KB'

const FileIcon = ({ name }: { name: string }) => {
  if (name.endsWith('.pdf')) return <DescriptionIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
  if (name.endsWith('.md'))  return <ArticleIcon      sx={{ fontSize: 18, color: 'text.secondary' }} />
  return <DescriptionIcon sx={{ fontSize: 18, color: 'text.secondary' }} />
}

const PROVIDER_CHIPS = [
  { label: 'Embed: Mistral',    color: 'primary'   as const },
  { label: 'Store: ChromaDB',   color: 'secondary' as const },
  { label: 'Chunk: Semantic',   color: 'default'   as const },
  { label: 'Generate: Mistral', color: 'primary'   as const },
]

export default function DropState({ onStart }: Props) {
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
    if (!files.length && !urls.length) {
      onStart([], ['https://docs.mistral.ai'])
    } else {
      onStart(files, urls)
    }
  }

  return (
    <Container maxWidth="lg" sx={{ py: 6 }}>
      <Stack spacing={3} alignItems="center">

        {/* Hero */}
        <Box textAlign="center">
          <Typography variant="overline" color="primary">
            Dr. Doofenshmirtz's greatest invention
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

        {/* Provider chips */}
        <Stack direction="row" spacing={1} flexWrap="wrap" justifyContent="center">
          {PROVIDER_CHIPS.map(({ label, color }, i) => (
            <Chip key={i} label={label} size="small" color={color} variant="outlined" />
          ))}
        </Stack>

        {/* CTA */}
        <Button
          variant="contained" color="primary" fullWidth size="large"
          endIcon={<span style={{ fontSize: 20 }}>›</span>}
          onClick={handleStart}
          sx={{ py: 1.5, fontSize: '0.95rem' }}
        >
          Start Raginator
        </Button>

      </Stack>
    </Container>
  )
}
