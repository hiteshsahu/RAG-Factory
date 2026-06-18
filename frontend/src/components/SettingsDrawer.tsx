import React from 'react'
import {
  Box, Drawer, IconButton, Stack,
  ToggleButton, ToggleButtonGroup, Typography,
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import type { PipelineSettings } from '../data'

interface Props {
  open: boolean
  settings: PipelineSettings
  onChange: (settings: PipelineSettings) => void
  onClose: () => void
}

interface Section {
  key: keyof PipelineSettings
  label: string
  hint: string
  options: readonly string[]
}

const SECTIONS: Section[] = [
  { key: 'chunkStrategy', label: 'Chunking strategy',  hint: 'Stage 1 — splits documents into retrievable chunks', options: ['Fixed', 'Recursive', 'Semantic', 'Code'] },
  { key: 'embedProvider', label: 'Embedding provider', hint: 'Stage 2 — converts chunks into vectors', options: ['Mistral', 'OpenAI', 'Ollama'] },
  { key: 'vectorStore',   label: 'Vector store',       hint: 'Stage 3 — persists vectors for similarity search', options: ['ChromaDB', 'pgvector'] },
  { key: 'llmProvider',   label: 'LLM for generation',  hint: 'Stage 6 — generates the final answer', options: ['Mistral', 'OpenAI', 'Ollama'] },
]

export default function SettingsDrawer({ open, settings, onChange, onClose }: Props) {
  const setValue = (key: keyof PipelineSettings, value: string | null) => {
    if (!value) return
    onChange({ ...settings, [key]: value } as PipelineSettings)
  }

  return (
    <Drawer anchor="right" open={open} onClose={onClose}>
      <Box sx={{ width: 320, p: 3 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={0.5}>
          <Typography variant="h6" fontWeight={600}>Pipeline settings</Typography>
          <IconButton size="small" onClick={onClose} aria-label="Close settings">
            <CloseIcon sx={{ fontSize: 18 }} />
          </IconButton>
        </Stack>
        <Typography variant="body2" color="text.secondary" mb={3}>
          Takes effect on the next run.
        </Typography>

        <Stack spacing={3}>
          {SECTIONS.map(section => (
            <Box key={section.key}>
              <Typography variant="body2" fontWeight={600}>{section.label}</Typography>
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
    </Drawer>
  )
}
