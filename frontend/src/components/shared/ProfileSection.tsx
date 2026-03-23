import type { ReactNode } from 'react'
import type { LucideIcon } from 'lucide-react'

export function ProfileSection({
  title,
  icon: Icon,
  children,
  padding = 'p-6',
}: {
  title?: string
  icon?: LucideIcon
  children: ReactNode
  padding?: string
}) {
  return (
    <div className={`rounded-2xl border border-border bg-card ${padding}`}>
      {title && (
        <h2 className="flex items-center gap-2 font-semibold text-[15px] text-foreground mb-3">
          {Icon && <Icon className="w-4 h-4 text-zinc-400" />}
          {title}
        </h2>
      )}
      {children}
    </div>
  )
}

export function ProfileSidebarCard({
  title,
  children,
}: {
  title: string
  children: ReactNode
}) {
  return (
    <div className="rounded-2xl border border-border bg-card p-5">
      <h3 className="font-semibold text-[15px] text-foreground mb-3">{title}</h3>
      {children}
    </div>
  )
}

export function QuickInfoRow({
  label,
  children,
}: {
  label: string
  children: ReactNode
}) {
  return (
    <div className="flex justify-between text-sm">
      <dt className="text-zinc-500">{label}</dt>
      <dd className="text-zinc-200 font-medium">{children}</dd>
    </div>
  )
}
