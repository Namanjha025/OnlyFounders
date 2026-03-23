import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import { AvatarRing } from './AvatarRing'

export function EntityCard({
  to,
  avatarContent,
  ringProgress,
  ringColor,
  name,
  subtitle,
  type,
  description,
  tags,
  badge,
}: {
  to: string
  avatarContent: ReactNode
  ringProgress: number
  ringColor: string
  name: string
  subtitle?: string | null
  type: string
  description?: string | null
  tags?: string[]
  badge?: boolean
}) {
  return (
    <Link
      to={to}
      className={cn(
        'group flex flex-col items-center rounded-2xl bg-card p-6',
        'border border-border transition-all duration-200',
        'hover:border-white/[0.12] hover:bg-white/[0.03]',
      )}
    >
      <div className="relative">
        <AvatarRing progress={ringProgress} color={ringColor}>
          {avatarContent}
        </AvatarRing>
        {badge && (
          <div className="absolute bottom-2.5 -right-0.5 w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center ring-2 ring-card z-10">
            <Check className="w-3 h-3 text-white" strokeWidth={3} />
          </div>
        )}
      </div>

      <p className="text-[15px] font-semibold text-foreground text-center leading-tight mb-0.5">
        {name}
      </p>
      {subtitle && (
        <p className="text-[13px] text-muted-foreground text-center leading-tight line-clamp-2">
          {subtitle}
        </p>
      )}
      <p className="text-[12px] text-muted-foreground capitalize mt-0.5">{type}</p>

      {description && (
        <p className="text-[13px] text-muted-foreground text-center line-clamp-2 leading-relaxed mt-2">
          {description}
        </p>
      )}

      {tags && tags.length > 0 && (
        <div className="flex flex-wrap justify-center gap-1 mt-2">
          {tags.slice(0, 3).map((tag, i) => (
            <span key={i} className="text-[11px] text-muted-foreground bg-secondary px-2 py-0.5 rounded-full">{tag}</span>
          ))}
          {tags.length > 3 && (
            <span className="text-[11px] text-muted-foreground">+{tags.length - 3}</span>
          )}
        </div>
      )}
    </Link>
  )
}
