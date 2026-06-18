import React from 'react'
import {
  Badge, Box, Drawer, IconButton, List, ListItemButton, ListItemText,
  Stack, Tooltip, Typography,
} from '@mui/material'
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import HistoryIcon from '@mui/icons-material/History'
import ManageSearchIcon from '@mui/icons-material/ManageSearch'
import type { Theme } from '@mui/material'

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
  onOpen: () => void
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

const MINI_WIDTH = 64
const FULL_WIDTH = 300

// Mini variant persistent drawer, mirroring SettingsDrawer on the other
// side: collapsed state stays mounted as a narrow icon rail (with an entry
// count badge) instead of disappearing entirely; expanding reveals the list.
export default function HistoryDrawer({ open, entries, activeId, onSelect, onClose, onOpen }: Props) {
  const width = open ? FULL_WIDTH : MINI_WIDTH
  const widthTransition = (theme: Theme) =>
    theme.transitions.create('width', { duration: theme.transitions.duration.shorter })

  return (
    <Drawer
      variant="persistent"
      anchor="left"
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
          {open && <Typography variant="h6" fontWeight={600}>History</Typography>}
          <Tooltip title={open ? 'Collapse' : 'Expand history'} placement="right">
            <IconButton size="small" onClick={open ? onClose : onOpen} aria-label={open ? 'Collapse history' : 'Expand history'}>
              {open ? <ChevronLeftIcon sx={{ fontSize: 18 }} /> : <ChevronRightIcon sx={{ fontSize: 18 }} />}
            </IconButton>
          </Tooltip>
        </Stack>

        {open ? (
          <Box sx={{ px: 2.5, pb: 3, overflowY: 'auto' }}>
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
        ) : (
          <Stack alignItems="center" sx={{ pt: 1 }}>
            <Tooltip title={entries.length ? `${entries.length} question${entries.length === 1 ? '' : 's'} in history` : 'No history yet'} placement="right">
              <IconButton size="small" onClick={onOpen} aria-label="Expand history">
                <Badge badgeContent={entries.length} color="primary" max={99} sx={{ '& .MuiBadge-badge': { fontSize: '0.6rem', height: 16, minWidth: 16 } }}>
                  <HistoryIcon sx={{ fontSize: 20, color: 'primary.main' }} />
                </Badge>
              </IconButton>
            </Tooltip>
          </Stack>
        )}
      </Box>
    </Drawer>
  )
}
