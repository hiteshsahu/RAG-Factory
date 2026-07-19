// Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
// SPDX-License-Identifier: Apache-2.0

import React, { useRef, useState } from 'react'
import {
  Alert, Box, Divider, IconButton, Stack, Tooltip,
  ToggleButton, ToggleButtonGroup, Typography,
} from '@mui/material'
import ContentCutIcon from '@mui/icons-material/ContentCut'
import FormatShapesIcon from '@mui/icons-material/FormatShapes';
import StorageIcon from '@mui/icons-material/Storage'
import PsychologyIcon from '@mui/icons-material/Psychology';
import type { PipelineSettings } from '../data'
import { providerIcon } from './icons/ProviderIcons'
import { vectorStoreIcon } from './icons/VectorStoreIcons'
import PersistentSidebar from './PersistentSidebar'

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
  { key: 'embedProvider', label: 'Embedding provider', hint: 'Stage 2 — converts chunks into vectors', icon: FormatShapesIcon, options: ['Mistral', 'OpenAI', 'Ollama'] },
  { key: 'vectorStore',   label: 'Vector store',       hint: 'Stage 3 — persists vectors for similarity search', icon: StorageIcon, options: ['ChromaDB', 'pgvector'] },
  { key: 'llmProvider',   label: 'LLM for generation',  hint: 'Stage 6 — generates the final answer', icon: PsychologyIcon, options: ['Mistral', 'OpenAI', 'Ollama'] },
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

  return (
    <>
      <PersistentSidebar
        anchor="right"
        open={open}
        onOpen={onOpen}
        onClose={onClose}
        title="Settings"
        fullWidth={FULL_WIDTH}
        miniWidth={MINI_WIDTH}
        collapsedContent={
          <Stack spacing={1} alignItems="center" sx={{ pt: 1 }}>
            {SECTIONS.map(section => (
              <Tooltip key={section.key} title={`${section.label}: ${settings[section.key]}`} placement="left">
                <IconButton size="medium" onClick={onOpen} aria-label={`Expand ${section.label}`}>
                  <section.icon sx={{ fontSize: 20, color: 'primary.main' }} />
                </IconButton>
              </Tooltip>
            ))}
          </Stack>
        }
      >
        <Box sx={{ px: 2.5, pb: 3, flex: 1, minHeight: 0, overflowY: 'auto' }}>
          <Typography variant="body2" color="text.secondary" mb={3}>
            Takes effect on the next run. Saved automatically.
          </Typography>

          <Stack spacing={3} divider={<Divider flexItem />}>
            {SECTIONS.map(section => (
              <Box key={section.key}>
                <Stack direction="row" alignItems="center" spacing={1} mb={0.25}>
                  <section.icon sx={{ fontSize: 20, color: 'primary.main' }} />
                  <Typography variant="body2" fontWeight={600}>{section.label}</Typography>
                </Stack>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                  {section.hint}
                </Typography>
                <ToggleButtonGroup
                  exclusive
                  size="small"
                  value={settings[section.key]}
                  onChange={(_, value) => setValue(section.key, value)}
                  sx={{
                    // 2 options always fit one row as a flex line. 3+ (the
                    // provider sections, and chunkStrategy's 4) don't fit
                    // this drawer's width on one line with icons -- flex-wrap
                    // left the last one stranded alone on its own row, only
                    // half as wide as the row above it. A real 2-column grid
                    // instead, so every button is the same width.
                    ...(section.options.length > 2
                      ? { display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)' }
                      : { display: 'flex', flexWrap: 'wrap' }),
                    gap: 0.75,
                    // ToggleButtonGroup's segmented-control CSS only rounds
                    // the literal first/last child in the DOM -- fine for a
                    // single row, but with wrapping, every wrapped-row edge
                    // button was left square. Give each button its own full
                    // radius and border instead of relying on DOM-order logic.
                    '& .MuiToggleButtonGroup-grouped': {
                      margin: 0,
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: '8px !important',
                    },
                  }}
                >
                  {section.options.map(opt => (
                    <ToggleButton
                      key={opt} value={opt}
                      sx={{
                        textTransform: 'none', fontSize: '0.8rem', px: 2, py: 0.75,
                        gap: 0.6,
                        // Default Mui-selected is a faint neutral tint --
                        // too low-contrast to read as "this one's active"
                        // at a glance. Solid fill instead.
                        '&.Mui-selected': {
                          bgcolor: 'primary.main',
                          color: '#fff',
                          '&:hover': { bgcolor: 'primary.dark' },
                        },
                      }}
                    >
                      {providerIcon(opt, 16) ?? vectorStoreIcon(opt, 16)}
                      {opt}
                    </ToggleButton>
                  ))}
                </ToggleButtonGroup>
              </Box>
            ))}
          </Stack>
        </Box>
      </PersistentSidebar>

      {/* Always visible regardless of open/collapsed -- a toast already
          in flight shouldn't vanish just because the drawer got collapsed. */}
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
    </>
  )
}
