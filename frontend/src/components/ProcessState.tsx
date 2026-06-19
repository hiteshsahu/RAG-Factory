import React, { useEffect, useRef } from 'react'
import {
  Alert, AlertTitle, Box, Button, Card, CircularProgress, Container,
  Grid, LinearProgress, Stack, ToggleButton, Tooltip, Typography,
} from '@mui/material'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import PlayCircleIcon from '@mui/icons-material/PlayCircle'
import PauseCircleIcon from '@mui/icons-material/PauseCircle'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import ContentCutIcon from '@mui/icons-material/ContentCut'
import FormatShapesIcon from '@mui/icons-material/FormatShapes'
import StorageIcon from '@mui/icons-material/Storage'
import ManageSearchIcon from '@mui/icons-material/ManageSearch'
import SortIcon from '@mui/icons-material/Sort'
import PsychologyIcon from '@mui/icons-material/Psychology'
import FactCheckIcon from '@mui/icons-material/FactCheck'
import { STAGES } from '../data'

interface LogLine { text: string; kind: 'default' | 'success' | 'error' }

// Same glyphs as SettingsDrawer's chunk/embed/store/generate sections where
// they overlap (stages 1, 2, 3, 6) -- one consistent icon language for the
// same underlying concept, instead of two different icons for "chunking".
const STAGE_ICON: Record<number, React.ElementType> = {
  0: CloudUploadIcon,
  1: ContentCutIcon,
  2: FormatShapesIcon,
  3: StorageIcon,
  4: ManageSearchIcon,
  5: SortIcon,
  6: PsychologyIcon,
  7: FactCheckIcon,
}

interface Props {
  stagesDone: number
  activeStage: number
  failedStage: number | null
  stageStats: Record<number, string>
  logs: LogLine[]
  // True only once the real 'complete' event has landed -- not the same
  // moment as "all 8 stage tiles show done", since suggestion generation
  // still runs server-side for a few seconds after the last stage_done.
  pipelineDone: boolean
  onRetry: () => void
  onReset: () => void
  autoAdvance: boolean
  onToggleAutoAdvance: () => void
  onContinue: () => void
}

export default function ProcessState({
  stagesDone, activeStage, failedStage, stageStats, logs, pipelineDone, onRetry, onReset,
  autoAdvance, onToggleAutoAdvance, onContinue,
}: Props) {
  const logRef = useRef<HTMLDivElement>(null)
  const failed = failedStage !== null
  const complete = pipelineDone && !failed

  useEffect(() => {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight
  }, [logs])

  const progress = Math.round((stagesDone / STAGES.length) * 100)

  return (
    <Container maxWidth="xl" sx={{ py: 6 }}>
      <Stack spacing={4}>

        {/* Overall progress */}
        <Box>
          <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1.5}>
            <Typography variant="body1" color="text.secondary" sx={{ fontFamily: '"JetBrains Mono",monospace' }}>
              Pipeline · {stagesDone} / {STAGES.length} stages
            </Typography>
            <Stack direction="row" spacing={1.5} alignItems="center">
              <Tooltip title={autoAdvance ? 'Auto-advances to chat when the pipeline finishes' : 'Stays here so you can see each stage’s result'}>
                <ToggleButton
                  value="autoAdvance"
                  selected={autoAdvance}
                  onChange={onToggleAutoAdvance}
                  size="small"
                  sx={{
                    textTransform: 'none', fontSize: '0.75rem', px: 1.5, py: 0.5, gap: 0.6,
                    border: '1px solid', borderColor: 'divider', borderRadius: '8px !important',
                    '&.Mui-selected': { bgcolor: 'primary.main', color: '#fff', '&:hover': { bgcolor: 'primary.dark' } },
                  }}
                >
                  {autoAdvance ? <PlayCircleIcon sx={{ fontSize: 16 }} /> : <PauseCircleIcon sx={{ fontSize: 16 }} />}
                  Auto-advance
                </ToggleButton>
              </Tooltip>
              <Typography variant="body1" color={failed ? 'error' : 'primary'} sx={{ fontFamily: '"JetBrains Mono",monospace', fontWeight: 600 }}>
                {failed ? 'failed' : `${progress}%`}
              </Typography>
            </Stack>
          </Stack>
          <LinearProgress variant="determinate" value={progress} color={failed ? 'error' : 'primary'} sx={{ height: 6, borderRadius: 3 }} />
        </Box>

        {/* Auto-advance paused -- pipeline is done, waiting for the user */}
        {complete && !autoAdvance && (
          <Alert
            severity="success"
            action={<Button color="inherit" size="small" variant="outlined" onClick={onContinue}>Continue to chat →</Button>}
          >
            Pipeline complete — review the stage results below, then continue when you're ready.
          </Alert>
        )}

        {/* Failure banner */}
        {failed && failedStage !== null && (
          <Alert
            severity="error"
            action={
              <Stack direction="row" spacing={1}>
                <Button color="inherit" size="small" onClick={onReset}>Back</Button>
                <Button color="inherit" size="small" variant="outlined" onClick={onRetry}>Retry</Button>
              </Stack>
            }
          >
            {failedStage >= 0 ? (
              <AlertTitle sx={{ fontWeight: 600 }}>
                Stage {failedStage} — {STAGES[failedStage].name} ({STAGES[failedStage].alias}) failed
              </AlertTitle>
            ) : (
              <AlertTitle sx={{ fontWeight: 600 }}>Failed before processing started</AlertTitle>
            )}
            <Stack spacing={0.5}>
              {logs.filter(l => l.kind === 'error').map((l, i) => (
                <Typography key={i} variant="body2" sx={{ fontFamily: '"JetBrains Mono",monospace', fontSize: '0.78rem' }}>
                  {l.text}
                </Typography>
              ))}
            </Stack>
          </Alert>
        )}

        {/* Stage tiles */}
        <Grid container spacing={2.5}>
          {STAGES.map((s, i) => {
            const isFailed = i === failedStage
            const done    = i < stagesDone
            const active  = !isFailed && i === activeStage && i >= stagesDone
            const waiting = !isFailed && i > activeStage
            const StageIcon = STAGE_ICON[s.num]

            return (
              <Grid item xs={6} sm={4} md={3} key={i}>
                <Card
                  sx={{
                    p: 2.5,
                    minHeight: 140,
                    opacity: waiting ? 0.45 : 1,
                    borderColor: isFailed
                      ? 'rgba(226,75,74,0.6)'
                      : done
                      ? 'rgba(29,158,117,0.4)'
                      : active
                      ? 'rgba(29,158,117,0.25)'
                      : 'rgba(255,255,255,0.08)',
                    bgcolor: isFailed ? 'rgba(226,75,74,0.08)' : done ? 'rgba(29,158,117,0.08)' : 'background.paper',
                    transition: 'all .3s',
                  }}
                >
                  <Stack spacing={1}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography
                        variant="body2"
                        sx={{ fontFamily: '"JetBrains Mono",monospace', color: isFailed ? 'error.main' : done || active ? 'primary.main' : 'text.secondary' }}
                      >
                        s{s.num}
                      </Typography>
                      {isFailed && <ErrorIcon sx={{ fontSize: 20, color: 'error.main' }} />}
                      {!isFailed && done   && <CheckCircleIcon sx={{ fontSize: 20, color: 'primary.main' }} />}
                      {!isFailed && active && <CircularProgress size={16} color="primary" />}
                    </Stack>

                    <Stack direction="row" spacing={1} alignItems="center">
                      <StageIcon
                        sx={{
                          fontSize: 22,
                          color: isFailed ? 'error.main' : done || active ? 'primary.main' : 'text.secondary',
                        }}
                      />
                      <Typography variant="h6" fontWeight={600}>{s.name}</Typography>
                    </Stack>

                    <Typography variant="body2" color="text.secondary" sx={{ fontFamily: '"JetBrains Mono",monospace', fontSize: '0.75rem' }}>
                      {s.alias}
                    </Typography>

                    <Typography
                      variant="body2"
                      sx={{
                        fontFamily: '"JetBrains Mono",monospace', fontSize: '0.75rem', mt: 0.5,
                        color: isFailed ? 'error.main' : done ? 'primary.main' : 'text.secondary',
                      }}
                    >
                      {isFailed ? 'failed' : done ? (stageStats[i] ?? s.stats) : active ? 'running…' : 'waiting…'}
                    </Typography>
                  </Stack>
                </Card>
              </Grid>
            )
          })}
        </Grid>

        {/* Log panel */}
        <Box
          ref={logRef}
          sx={{
            p: 3,
            fontFamily: '"JetBrains Mono",monospace',
            fontSize: '0.85rem',
            lineHeight: 2,
            maxHeight: 280,
            overflowY: 'auto',
            bgcolor: '#080809',
            border: '0.5px solid rgba(255,255,255,0.06)',
            borderRadius: 2,
          }}
        >
          {logs.length === 0 ? (
            <Box sx={{ color: 'rgba(255,255,255,0.2)' }}>› initialising…</Box>
          ) : (
            logs.map((l, i) => (
              <Box
                key={i}
                sx={{
                  color: l.kind === 'success' ? 'primary.main' : l.kind === 'error' ? 'error.main' : 'rgba(255,255,255,0.35)',
                  fontWeight: l.kind === 'error' ? 600 : 400,
                }}
              >
                › {l.text}
              </Box>
            ))
          )}
        </Box>

      </Stack>
    </Container>
  )
}
