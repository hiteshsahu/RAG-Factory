import SvgIcon from '@mui/material/SvgIcon'
import type { SvgIconProps } from '@mui/material/SvgIcon'

// Unlike Mistral/OpenAI/Ollama, neither ChromaDB nor pgvector has a logo in
// any brand-icon set checked (lobehub, simple-icons) -- both are AI-model-
// provider focused, not vector-store focused, and pgvector isn't really its
// own brand (it's a Postgres extension). Original glyphs instead: Chroma
// evokes "color" (its namesake) via three tinted dots; pgvector evokes
// "Postgres + vector" via a database cylinder in Postgres's own blue.
export function ChromaDBIcon(props: SvgIconProps) {
  return (
    <SvgIcon {...props} viewBox="0 0 24 24">
      <circle cx="8" cy="9" r="4.2" fill="#FF6B35" />
      <circle cx="16" cy="9" r="4.2" fill="#E94BA0" />
      <circle cx="12" cy="16" r="4.2" fill="#2DD4BF" />
    </SvgIcon>
  )
}

export function PgVectorIcon(props: SvgIconProps) {
  return (
    <SvgIcon {...props} viewBox="0 0 24 24">
      <g fill="none" stroke="#336791" strokeWidth="1.8" strokeLinecap="round">
        <ellipse cx="12" cy="6" rx="7" ry="2.5" />
        <path d="M5 6v12c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5V6" />
        <path d="M5 11c0 1.4 3.1 2.5 7 2.5s7-1.1 7-2.5" />
      </g>
      <circle cx="9.5" cy="17" r="1.1" fill="#336791" />
      <circle cx="14.5" cy="17" r="1.1" fill="#336791" />
    </SvgIcon>
  )
}

const VECTOR_STORE_ICON: Record<string, React.ElementType<SvgIconProps>> = {
  ChromaDB: ChromaDBIcon,
  pgvector: PgVectorIcon,
}

export function vectorStoreIcon(name: string, size: number): React.ReactElement | undefined {
  const Icon = VECTOR_STORE_ICON[name]
  return Icon ? <Icon sx={{ fontSize: size }} /> : undefined
}
