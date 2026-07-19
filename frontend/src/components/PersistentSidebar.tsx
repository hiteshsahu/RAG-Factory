// Copyright 2026 Hitesh Kumar Sahu — https://hiteshsahu.com
// SPDX-License-Identifier: Apache-2.0

import React from 'react'
import { Box, Drawer, IconButton, Stack, Tooltip, Typography } from '@mui/material'
import type { SxProps, Theme } from '@mui/material'
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft'
import ChevronRightIcon from '@mui/icons-material/ChevronRight'

interface Props {
  anchor: 'left' | 'right'
  open: boolean
  onOpen: () => void
  onClose: () => void
  title: string
  fullWidth: number
  miniWidth?: number
  // Per-instance tweak layered on top of the shared header padding (e.g.
  // HistoryDrawer wants a tighter bottom gap before its "New corpus"
  // button than SettingsDrawer needs before its section list).
  headerSx?: SxProps<Theme>
  children: React.ReactNode
  collapsedContent: React.ReactNode
}

const DEFAULT_MINI_WIDTH = 64

// Shared chrome for HistoryDrawer/SettingsDrawer -- both are a "persistent"
// drawer that never fully hides, just narrows to an icon rail
// (`collapsedContent`), with a title + collapse/expand chevron header. Only
// that shell + width/transition math is common; the actual content (corpus
// list vs. settings sections) stays with each caller.
export default function PersistentSidebar({
  anchor, open, onOpen, onClose, title, fullWidth, miniWidth = DEFAULT_MINI_WIDTH,
  headerSx, children, collapsedContent,
}: Props) {
  const width = open ? fullWidth : miniWidth
  const widthTransition = (theme: Theme) =>
    theme.transitions.create('width', { duration: theme.transitions.duration.shorter })

  // Open: chevron points toward the edge it's anchored to (closing
  // direction). Closed: points back into the page (opening direction).
  const CollapseIcon = anchor === 'left' ? ChevronLeftIcon : ChevronRightIcon
  const ExpandIcon = anchor === 'left' ? ChevronRightIcon : ChevronLeftIcon
  const tooltipPlacement = anchor === 'left' ? 'right' : 'left'
  const lowerTitle = title.toLowerCase()

  return (
    <Drawer
      variant="persistent"
      anchor={anchor}
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
          sx={{ px: open ? 2.5 : 1, py: 2, ...headerSx }}
        >
          {open && <Typography variant="h6" fontWeight={600}>{title}</Typography>}
          <Tooltip title={open ? 'Collapse' : `Expand ${lowerTitle}`} placement={tooltipPlacement}>
            <IconButton
              size="small"
              onClick={open ? onClose : onOpen}
              aria-label={open ? `Collapse ${lowerTitle}` : `Expand ${lowerTitle}`}
            >
              {open ? <CollapseIcon sx={{ fontSize: 18 }} /> : <ExpandIcon sx={{ fontSize: 18 }} />}
            </IconButton>
          </Tooltip>
        </Stack>

        {open ? children : collapsedContent}
      </Box>
    </Drawer>
  )
}
