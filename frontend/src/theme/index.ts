import { createTheme } from '@mui/material/styles'
import type { PaletteMode } from '@mui/material'

const getTheme = (mode: PaletteMode) => {
  const dark = mode === 'dark'

  // Light mode's hairline/background values are deliberately stronger than
  // dark mode's -- at the same low opacity used for dark mode, borders and
  // the default/paper background split were nearly invisible on white,
  // making the whole UI read as flat and washed out.
  const hairline = dark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.14)'
  const scrollbar = dark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.24)'

  return createTheme({
    palette: {
      mode,
      primary:    { main: '#1D9E75' },
      secondary:  { main: '#7F77DD' },
      error:      { main: '#E24B4A' },
      background: dark
        ? { default: '#0d0d0f', paper: '#141418' }
        : { default: '#e9eaee', paper: '#ffffff' },
      text: dark
        ? { primary: '#e8e8f0', secondary: '#888898' }
        : { primary: '#14141a', secondary: '#4d4d5c' },
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
        // Outlined chips render palette[color].main directly as both text and
        // border. primary/secondary's raw values are tuned for dark paper
        // (~3.5:1 against white) -- too low for small chip text in light
        // mode, so swap in darker shades of the same hues there.
        variants: dark ? [] : [
          {
            props: { variant: 'outlined', color: 'primary' },
            style: { color: '#137055', borderColor: 'rgba(19,112,85,0.5)' },
          },
          {
            props: { variant: 'outlined', color: 'secondary' },
            style: { color: '#4F46C2', borderColor: 'rgba(79,70,194,0.5)' },
          },
        ],
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            backgroundImage: 'none',
            borderBottom: `0.5px solid ${hairline}`,
            backgroundColor: dark ? 'rgba(13,13,15,0.92)' : 'rgba(255,255,255,0.92)',
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
