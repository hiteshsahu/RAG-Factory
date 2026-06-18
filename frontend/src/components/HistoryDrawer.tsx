import React from 'react'
import {
  Box, Drawer, IconButton, List, ListItemButton, ListItemText,
  Stack, Typography,
} from '@mui/material'
import CloseIcon from '@mui/icons-material/Close'
import ManageSearchIcon from '@mui/icons-material/ManageSearch'

export interface HistoryEntry {
  id:    number
  query: string
  time:  number
}

interface Props {
  open: boolean
  entries: HistoryEntry[]
  activeId: number | null
  onSelect: (entry: HistoryEntry) => void
  onClose: () => void
}

const relativeTime = (ts: number) => {
  const seconds = Math.round((Date.now() - ts) / 1000)
  if (seconds < 5) return 'just now'
  if (seconds < 60) return `${seconds}s ago`
  const minutes = Math.round(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.round(minutes / 60)
  return `${hours}h ago`
}

const DRAWER_WIDTH = 300

export default function HistoryDrawer({ open, entries, activeId, onSelect, onClose }: Props) {
  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      onClose={onClose}
      sx={{
        width: open ? DRAWER_WIDTH : 0,
        flexShrink: 0,
        overflowX: 'hidden',
        transition: theme => theme.transitions.create('width', { duration: theme.transitions.duration.shorter }),
        '& .MuiDrawer-paper': { width: DRAWER_WIDTH, boxSizing: 'border-box', position: 'relative' },
      }}
    >
      <Box sx={{ width: DRAWER_WIDTH, p: 2.5 }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" fontWeight={600}>History</Typography>
          <IconButton size="small" onClick={onClose} aria-label="Close history">
            <CloseIcon sx={{ fontSize: 18 }} />
          </IconButton>
        </Stack>

        {entries.length === 0 ? (
          <Stack alignItems="center" sx={{ opacity: 0.4, py: 6 }} spacing={1}>
            <ManageSearchIcon sx={{ fontSize: 32 }} />
            <Typography variant="body2" color="text.secondary" textAlign="center">
              No questions yet. Ask something to build history.
            </Typography>
          </Stack>
        ) : (
          <List disablePadding>
            {entries.map(entry => (
              <ListItemButton
                key={entry.id}
                selected={entry.id === activeId}
                onClick={() => onSelect(entry)}
                sx={{
                  borderRadius: 1.5, mb: 0.5, alignItems: 'flex-start',
                  '&.Mui-selected': { bgcolor: 'rgba(29,158,117,0.12)' },
                }}
              >
                <ListItemText
                  primary={entry.query}
                  secondary={relativeTime(entry.time)}
                  primaryTypographyProps={{
                    variant: 'body2', fontWeight: 500,
                    sx: { display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' },
                  }}
                  secondaryTypographyProps={{
                    variant: 'caption', sx: { fontFamily: '"JetBrains Mono",monospace', fontSize: '0.68rem' },
                  }}
                />
              </ListItemButton>
            ))}
          </List>
        )}
      </Box>
    </Drawer>
  )
}
