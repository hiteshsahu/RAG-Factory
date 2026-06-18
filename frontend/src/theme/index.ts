import { createTheme, type PaletteMode } from '@mui/material/styles'

const getTheme = (mode: PaletteMode) => {
  const dark = mode === 'dark'

  const hairline = dark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'
  const scrollbar = dark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.18)'

  return createTheme({
    palette: {
      mode,
      primary:    { main: '#1D9E75' },
      secondary:  { main: '#7F77DD' },
      error:      { main: '#E24B4A' },
      background: dark
        ? { default: '#0d0d0f', paper: '#141418' }
        : { default: '#f6f6f8', paper: '#ffffff' },
      text: dark
        ? { primary: '#e8e8f0', secondary: '#888898' }
        : { primary: '#16161a', secondary: '#5b5b6a' },
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
          '::-webkit-scrollbar-thumb': { background: scrollbar, borderRadius: 2 },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: { backgroundImage: 'none', border: `0.5px solid ${hairline}` },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: { backgroundImage: 'none', border: `0.5px solid ${hairline}` },
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
            borderBottom: `0.5px solid ${hairline}`,
            backgroundColor: dark ? 'rgba(13,13,15,0.92)' : 'rgba(255,255,255,0.85)',
            backdropFilter: 'blur(12px)',
          },
        },
      },
      MuiLinearProgress: {
        styleOverrides: {
          root: { borderRadius: 2, height: 3, backgroundColor: hairline },
        },
      },
      MuiButton: {
        styleOverrides: { root: { textTransform: 'none', fontWeight: 500 } },
      },
    },
  })
}

export default getTheme
