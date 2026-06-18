import React, { useRef, useState } from 'react'
import {
  Alert, Box, Drawer, IconButton, Stack, Tooltip,
  ToggleButton, ToggleButtonGroup, Typography,
} from '@mui/material'
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import ContentCutIcon from '@mui/icons-material/ContentCut'
import BubbleChartIcon from '@mui/icons-material/BubbleChart'
import StorageIcon from '@mui/icons-material/Storage'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import type { Theme } from '@mui/material'
import type { PipelineSettings } from '../data'

const TOAST_LIFETIME_MS = 2500
const MINI_WIDTH = 64
const FULL_WIDTH = 320

interface Props {
  open: boolean
  settings: PipelineSettings
  onChange: (settings: PipelineSettings) => void
  onClose: () => void
  onOpen: () => void
}

interface Section {
  key: keyof PipelineSettings
  label: string
  hint: string
  icon: React.ElementType
  options: readonly string[]
}

const SECTIONS: Section[] = [
  { key: 'chunkStrategy', label: 'Chunking strategy',  hint: 'Stage 1 — splits documents into retrievable chunks', icon: ContentCutIcon, options: ['Fixed', 'Recursive', 'Semantic', 'Code'] },
  { key: 'embedProvider', label: 'Embedding provider', hint: 'Stage 2 — converts chunks into vectors', icon: BubbleChartIcon, options: ['Mistral', 'OpenAI', 'Ollama'] },
  { key: 'vectorStore',   label: 'Vector store',       hint: 'Stage 3 — persists vectors for similarity search', icon: StorageIcon, options: ['ChromaDB', 'pgvector'] },
  { key: 'llmProvider',   label: 'LLM for generation',  hint: 'Stage 6 — generates the final answer', icon: SmartToyIcon, options: ['Mistral', 'OpenAI', 'Ollama'] },
]

// Mini variant persistent drawer: collapsed state stays mounted and visible
// as a narrow icon rail (never fully hidden, unlike a temporary/overlay
// drawer) so the current provider/strategy icons are always glanceable;
// expanding reveals the full toggle groups.
export default function SettingsDrawer({ open, settings, onChange, onClose, onOpen }: Props) {
  // Newest pushed to the end -- rendered last in a column flex layout, which
  // puts it nearest the bottom-left anchor; older toasts get visually pushed
  // up as new ones arrive, instead of replacing each other.
  const [toasts, setToasts] = useState<{ id: number; message: string }[]>([])
  const toastIdRef = useRef(0)

  const dismissToast = (id: number) => setToasts(t => t.filter(x => x.id !== id))

  const pushToast = (message: string) => {
    const id = ++toastIdRef.current
    setToasts(t => [...t, { id, message }])
    setTimeout(() => dismissToast(id), TOAST_LIFETIME_MS)
  }

  const setValue = (key: keyof PipelineSettings, value: string | null) => {
    if (!value || value === settings[key]) return
    onChange({ ...settings, [key]: value } as PipelineSettings)
    const section = SECTIONS.find(s => s.key === key)
    pushToast(`${section?.label ?? key} → ${value}`)
  }

  const width = open ? FULL_WIDTH : MINI_WIDTH
  const widthTransition = (theme: Theme) =>
    theme.transitions.create('width', { duration: theme.transitions.duration.shorter })

  return (
    <Drawer
      variant="persistent"
      anchor="right"
      open
      sx={{
        width,
        flexShrink: 0,
        overflowX: 'hidden',
        transition: widthTransition,
        '& .MuiDrawer-paper': {
          width, boxSizing: 'border-box', position: 'relative', overflowX: 'hidden',
          transition: widthTransition,
        },
      }}
    >
      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Stack
          direction="row" alignItems="center"
          justifyContent={open ? 'space-between' : 'center'}
          sx={{ px: open ? 2.5 : 1, py: 2 }}
        >
          {open && <Typography variant="h6" fontWeight={600}>Settings</Typography>}
          <Tooltip title={open ? 'Collapse' : 'Expand settings'} placement="left">
            <IconButton size="small" onClick={open ? onClose : onOpen} aria-label={open ? 'Collapse settings' : 'Expand settings'}>
              {open ? <ChevronRightIcon sx={{ fontSize: 18 }} /> : <ChevronLeftIcon sx={{ fontSize: 18 }} />}
            </IconButton>
          </Tooltip>
        </Stack>

        {open ? (
          <Box sx={{ px: 2.5, pb: 3, overflowY: 'auto' }}>
            <Typography variant="body2" color="text.secondary" mb={3}>
              Takes effect on the next run. Saved automatically.
            </Typography>

            <Stack spacing={3}>
              {SECTIONS.map(section => (
                <Box key={section.key}>
                  <Stack direction="row" alignItems="center" spacing={1} mb={0.25}>
                    <section.icon sx={{ fontSize: 18, color: 'primary.main' }} />
                    <Typography variant="body2" fontWeight={600}>{section.label}</Typography>
                  </Stack>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                    {section.hint}
                  </Typography>
                  <ToggleButtonGroup
                    exclusive
                    size="small"
                    fullWidth
                    value={settings[section.key]}
                    onChange={(_, value) => setValue(section.key, value)}
                    sx={{ flexWrap: 'wrap' }}
                  >
                    {section.options.map(opt => (
                      <ToggleButton key={opt} value={opt} sx={{ textTransform: 'none', flex: '1 0 auto' }}>
                        {opt}
                      </ToggleButton>
                    ))}
                  </ToggleButtonGroup>
                </Box>
              ))}
            </Stack>
          </Box>
        ) : (
          <Stack spacing={1} alignItems="center" sx={{ pt: 1 }}>
            {SECTIONS.map(section => (
              <Tooltip key={section.key} title={`${section.label}: ${settings[section.key]}`} placement="left">
                <IconButton size="small" onClick={onOpen} aria-label={`Expand ${section.label}`}>
                  <section.icon sx={{ fontSize: 20, color: 'primary.main' }} />
                </IconButton>
              </Tooltip>
            ))}
          </Stack>
        )}
      </Box>

      <Box
        sx={{
          position: 'fixed', bottom: 16, left: 16, zIndex: 1500,
          display: 'flex', flexDirection: 'column', gap: 1, maxWidth: 320,
        }}
      >
        {toasts.map(t => (
          <Alert
            key={t.id}
            severity="success" variant="filled"
            onClose={() => dismissToast(t.id)}
            sx={{ fontSize: '0.8rem' }}
          >
            {t.message}
          </Alert>
        ))}
      </Box>
    </Drawer>
  )
}
