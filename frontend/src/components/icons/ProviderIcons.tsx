import Box from '@mui/material/Box'
import type { BoxProps } from '@mui/material/Box'
import mistralColorSvg from '@lobehub/icons-static-svg/icons/mistral-color.svg?raw'
import openaiSvg from '@lobehub/icons-static-svg/icons/openai.svg?raw'
import ollamaSvg from '@lobehub/icons-static-svg/icons/ollama.svg?raw'

// Real brand marks from @lobehub/icons-static-svg (plain SVG files, zero
// runtime deps -- unlike the `@lobehub/icons` React package, which drags in
// antd + antd-style + a React 19 peer dep just for its Avatar/Combine
// wrappers).
function InlineSvgIcon({ svg, sx, ...props }: BoxProps & { svg: string }) {
  return (
    <Box
      component="span"
      {...props}
      sx={{ display: 'inline-flex', lineHeight: 0, '& svg': { display: 'block' }, ...sx }}
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  )
}

// Mistral ships a real multi-color mark (gold -> red gradient blocks), used
// as-is -- contrasts fine against any background. OpenAI and Ollama only
// have a plain black "currentColor" mark, so each gets a fixed flat accent
// set as this element's own `color` (not inherited) so they stay colorful
// and recognizable while unselected. Once *selected* though, that fixed
// accent sits on the solid primary-green ToggleButton fill -- teal-on-green
// in particular reads as muddy/low-contrast -- so flip back to the
// button's own white selected-text color via the ".Mui-selected &" escape.
export const MistralIcon = (props: BoxProps) => <InlineSvgIcon svg={mistralColorSvg} {...props} />
export const OpenAIIcon = ({ sx, ...props }: BoxProps) => (
  <InlineSvgIcon svg={openaiSvg} sx={{ color: '#74AA9C', '.Mui-selected &': { color: '#fff' }, ...sx }} {...props} />
)
export const OllamaIcon = ({ sx, ...props }: BoxProps) => (
  <InlineSvgIcon svg={ollamaSvg} sx={{ color: '#A87C4F', '.Mui-selected &': { color: '#fff' }, ...sx }} {...props} />
)

export const PROVIDER_ICON: Record<string, React.ElementType<BoxProps>> = {
  Mistral: MistralIcon,
  OpenAI: OpenAIIcon,
  Ollama: OllamaIcon,
}

// Every call site just wants "this provider's icon at this size, or nothing"
// -- folds the lookup + missing-icon guard that was repeated at each of the
// 4 places a provider name is rendered (AppBar chip, DropState chips, the
// embedding-model stat, SettingsDrawer's toggle buttons) into one helper.
export function providerIcon(provider: string, size: number): React.ReactElement | undefined {
  const Icon = PROVIDER_ICON[provider]
  return Icon ? <Icon sx={{ fontSize: size }} /> : undefined
}
