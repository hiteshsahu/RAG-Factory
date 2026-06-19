import React, { useState } from 'react'
import {
  Badge, Box, Button, Collapse, Divider, Drawer, IconButton, List, ListItemButton, ListItemText,
  Stack, Tooltip, Typography,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'
import DescriptionIcon from '@mui/icons-material/Description'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import HistoryIcon from '@mui/icons-material/History'
import LinkIcon from '@mui/icons-material/Link'
import ManageSearchIcon from '@mui/icons-material/ManageSearch'
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf'
import type { Theme } from '@mui/material'
import type { Message } from '../data'

export type SourceType = 'pdf' | 'doc' | 'url'

export interface HistoryQuery {
  id: number
  question: string
  messages: Message[]
  timestamp: number
}

export interface CorpusHistory {
  corpusId: string
  corpusName: string
  sourceType: SourceType
  docCount: number
  createdAt: number
  queries: HistoryQuery[]
}

interface Props {
  open: boolean
  corpora: CorpusHistory[]
  activeCorpusId: string | null
  activeQueryId: number | null
  onSelect: (corpusId: string, queryId: number) => void
  onNew: () => void
  onClose: () => void
  onOpen: () => void
}

const SOURCE_ICON: Record<SourceType, { icon: React.ElementType; color: string }> = {
  pdf: { icon: PictureAsPdfIcon, color: '#4C8DFF' },
  doc: { icon: DescriptionIcon, color: '#1D9E75' },
  url: { icon: LinkIcon, color: '#E2A53A' },
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
// side: collapsed state stays mounted as a narrow icon rail (with a query
// count badge) instead of disappearing entirely; expanding reveals the list,
// grouped by corpus -- you're not remembering queries, you're remembering
// conversations with a document.
export default function HistoryDrawer({
  open, corpora, activeCorpusId, activeQueryId, onSelect, onNew, onClose, onOpen,
}: Props) {
  // Starts with everything collapsed except whichever corpus is currently
  // active (the one you're actually chatting in) -- seeded once from
  // whatever was already in `corpora` on mount, so reopening the app with
  // existing history doesn't dump every past conversation open at once.
  const [collapsedIds, setCollapsedIds] = useState<Set<string>>(
    () => new Set(corpora.filter(c => c.corpusId !== activeCorpusId).map(c => c.corpusId)),
  )
  const toggleCollapsed = (corpusId: string) =>
    setCollapsedIds(prev => {
      const next = new Set(prev)
      if (next.has(corpusId)) next.delete(corpusId)
      else next.add(corpusId)
      return next
    })

  const width = open ? FULL_WIDTH : MINI_WIDTH
  const widthTransition = (theme: Theme) =>
    theme.transitions.create('width', { duration: theme.transitions.duration.shorter })
  const totalQueries = corpora.reduce((sum, c) => sum + c.queries.length, 0)

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
          sx={{ px: open ? 2.5 : 1, py: 2, pb: open ? 1 : 2 }}
        >
          {open && <Typography variant="h6" fontWeight={600}>History</Typography>}
          <Tooltip title={open ? 'Collapse' : 'Expand history'} placement="right">
            <IconButton size="small" onClick={open ? onClose : onOpen} aria-label={open ? 'Collapse history' : 'Expand history'}>
              {open ? <ChevronLeftIcon sx={{ fontSize: 18 }} /> : <ChevronRightIcon sx={{ fontSize: 18 }} />}
            </IconButton>
          </Tooltip>
        </Stack>

        {open && (
          <Box sx={{ px: 2.5, pb: 1.5 }}>
            <Button
              fullWidth size="small" variant="outlined"
              startIcon={<AddIcon sx={{ fontSize: 16 }} />}
              onClick={onNew}
              sx={{ justifyContent: 'flex-start', textTransform: 'none', fontWeight: 500 }}
            >
              New corpus
            </Button>
          </Box>
        )}

        {open && <Divider />}

        {open ? (
          <Box sx={{ px: 1.5, pb: 3, overflowY: 'auto' }}>
            {corpora.length === 0 ? (
              <Stack alignItems="center" sx={{ opacity: 0.4, py: 6 }} spacing={1}>
                <ManageSearchIcon sx={{ fontSize: 32 }} />
                <Typography variant="body2" color="text.secondary" textAlign="center">
                  No questions yet. Ask something to build history.
                </Typography>
              </Stack>
            ) : (
              <Stack spacing={2} divider={<Divider flexItem />} sx={{ pt: 2 }}>
                {corpora.map(corpus => {
                  const { icon: SourceIcon, color } = SOURCE_ICON[corpus.sourceType]
                  const collapsed = collapsedIds.has(corpus.corpusId)
                  return (
                    <Box key={corpus.corpusId}>
                      <Stack
                        direction="row" alignItems="flex-start" spacing={1}
                        onClick={() => toggleCollapsed(corpus.corpusId)}
                        sx={{ px: 1, mb: 0.5, py: 0.5, borderRadius: 1, cursor: 'pointer', '&:hover': { bgcolor: 'action.hover' } }}
                      >
                        <SourceIcon sx={{ fontSize: 18, color, mt: '2px', flexShrink: 0 }} />
                        <Box sx={{ minWidth: 0, flex: 1 }}>
                          <Typography
                            variant="body2" fontWeight={600}
                            sx={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
                          >
                            {corpus.corpusName}
                          </Typography>
                          <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.68rem', display: 'block' }}>
                            {corpus.docCount} doc{corpus.docCount === 1 ? '' : 's'} · {relativeTime(corpus.createdAt)}
                          </Typography>
                        </Box>
                        <ExpandMoreIcon
                          sx={{
                            fontSize: 18, mt: '2px', flexShrink: 0, color: 'text.secondary',
                            transform: collapsed ? 'rotate(-90deg)' : 'none',
                            transition: theme => theme.transitions.create('transform', { duration: theme.transitions.duration.shortest }),
                          }}
                        />
                      </Stack>

                      <Collapse in={!collapsed} timeout="auto">
                        {/* Vertical guide descending from the corpus icon --
                            without it, queries just looked like sibling list
                            items, not children of the corpus above them. */}
                        <Box sx={{ ml: '17px', pl: 1.5, borderLeft: '2px solid', borderColor: 'divider' }}>
                        <List disablePadding>
                          {corpus.queries.map(q => {
                            const active = corpus.corpusId === activeCorpusId && q.id === activeQueryId
                            return (
                              <ListItemButton
                                key={q.id}
                                selected={active}
                                onClick={() => onSelect(corpus.corpusId, q.id)}
                                sx={{
                                  borderRadius: 1.5, mb: 0.5, alignItems: 'flex-start',
                                  borderLeft: '2px solid',
                                  borderLeftColor: active ? 'primary.main' : 'transparent',
                                  '&.Mui-selected': { bgcolor: 'rgba(29,158,117,0.12)' },
                                }}
                              >
                                <ListItemText
                                  primary={q.question}
                                  secondary={relativeTime(q.timestamp)}
                                  primaryTypographyProps={{
                                    variant: 'body2', fontWeight: 500,
                                    sx: { display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' },
                                  }}
                                  secondaryTypographyProps={{
                                    variant: 'caption', sx: { fontFamily: '"JetBrains Mono",monospace', fontSize: '0.65rem' },
                                  }}
                                />
                              </ListItemButton>
                            )
                          })}
                        </List>
                        </Box>
                      </Collapse>
                    </Box>
                  )
                })}
              </Stack>
            )}
          </Box>
        ) : (
          <Stack spacing={1} alignItems="center" sx={{ pt: 1 }}>
            <Tooltip title="New corpus" placement="right">
              <IconButton size="small" onClick={onNew} aria-label="Start a new corpus">
                <AddIcon sx={{ fontSize: 20 }} />
              </IconButton>
            </Tooltip>
            <Tooltip title={totalQueries ? `${totalQueries} question${totalQueries === 1 ? '' : 's'} in history` : 'No history yet'} placement="right">
              <IconButton size="small" onClick={onOpen} aria-label="Expand history">
                <Badge badgeContent={totalQueries} color="primary" max={99} sx={{ '& .MuiBadge-badge': { fontSize: '0.6rem', height: 16, minWidth: 16 } }}>
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
