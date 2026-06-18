import { createTheme } from '@mui/material/styles'

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary:    { main: '#1D9E75' },
    secondary:  { main: '#7F77DD' },
    error:      { main: '#E24B4A' },
    background: { default: '#0d0d0f', paper: '#141418' },
    text:       { primary: '#e8e8f0', secondary: '#888898' },
  },
  typography: {
    fontFamily: '"Roboto", sans-serif',
    h4: { fontWeight: 600, letterSpacing: '-0.02em' },
    h6: { fontWeight: 500 },
    overline: { letterSpacing: '0.12em', fontSize: '0.7rem' },
  },
  shape: { borderRadius: 10 },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        '*': { boxSizing: 'border-box' },
        '::-webkit-scrollbar': { width: 4, height: 4 },
        '::-webkit-scrollbar-track': { background: 'transparent' },
        '::-webkit-scrollbar-thumb': { background: 'rgba(255,255,255,0.12)', borderRadius: 2 },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: 'none', border: '0.5px solid rgba(255,255,255,0.08)' },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: { backgroundImage: 'none', border: '0.5px solid rgba(255,255,255,0.08)' },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: { fontFamily: '"JetBrains Mono", monospace', fontSize: '0.7rem' },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          borderBottom: '0.5px solid rgba(255,255,255,0.08)',
          backgroundColor: 'rgba(13,13,15,0.92)',
          backdropFilter: 'blur(12px)',
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: { borderRadius: 2, height: 3, backgroundColor: 'rgba(255,255,255,0.08)' },
      },
    },
    MuiButton: {
      styleOverrides: { root: { textTransform: 'none', fontWeight: 500 } },
    },
  },
})

export default theme
