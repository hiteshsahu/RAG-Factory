import React, { useEffect, useRef } from 'react'
import {
  Box, Card, CircularProgress, Container,
  Grid, LinearProgress, Stack, Typography,
} from '@mui/material'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import { STAGES } from '../data'

interface LogLine { text: string; ok: boolean }

interface Props {
  stagesDone: number
  activeStage: number
  logs: LogLine[]
}

export default function ProcessState({ stagesDone, activeStage, logs }: Props) {
  const logRef = useRef<HTMLDivElement>(null)

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
            <Typography variant="body1" color="primary" sx={{ fontFamily: '"JetBrains Mono",monospace', fontWeight: 600 }}>
              {progress}%
            </Typography>
          </Stack>
          <LinearProgress variant="determinate" value={progress} color="primary" sx={{ height: 6, borderRadius: 3 }} />
        </Box>

        {/* Stage tiles */}
        <Grid container spacing={2.5}>
          {STAGES.map((s, i) => {
            const done    = i < stagesDone
            const active  = i === activeStage && i >= stagesDone
            const waiting = i > activeStage

            return (
              <Grid item xs={6} sm={4} md={3} key={i}>
                <Card
                  sx={{
                    p: 2.5,
                    minHeight: 140,
                    opacity: waiting ? 0.45 : 1,
                    borderColor: done
                      ? 'rgba(29,158,117,0.4)'
                      : active
                      ? 'rgba(29,158,117,0.25)'
                      : 'rgba(255,255,255,0.08)',
                    bgcolor: done ? 'rgba(29,158,117,0.08)' : 'background.paper',
                    transition: 'all .3s',
                  }}
                >
                  <Stack spacing={1}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography
                        variant="body2"
                        sx={{ fontFamily: '"JetBrains Mono",monospace', color: done || active ? 'primary.main' : 'text.secondary' }}
                      >
                        s{s.num}
                      </Typography>
                      {done   && <CheckCircleIcon sx={{ fontSize: 20, color: 'primary.main' }} />}
                      {active && <CircularProgress size={16} color="primary" />}
                    </Stack>

                    <Typography variant="h6" fontWeight={600}>{s.name}</Typography>

                    <Typography variant="body2" color="text.secondary" sx={{ fontFamily: '"JetBrains Mono",monospace', fontSize: '0.75rem' }}>
                      {s.alias}
                    </Typography>

                    <Typography
                      variant="body2"
                      sx={{ fontFamily: '"JetBrains Mono",monospace', fontSize: '0.75rem', mt: 0.5, color: done ? 'primary.main' : 'text.secondary' }}
                    >
                      {done ? s.stats : active ? 'running…' : 'waiting…'}
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
              <Box key={i} sx={{ color: l.ok ? 'primary.main' : 'rgba(255,255,255,0.35)' }}>
                › {l.text}
              </Box>
            ))
          )}
        </Box>

      </Stack>
    </Container>
  )
}
