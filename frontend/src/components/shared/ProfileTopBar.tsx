import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'

export function ProfileTopBar({
  backTo,
  backLabel,
  action,
}: {
  backTo: string
  backLabel: string
  action?: ReactNode
}) {
  return (
    <div className="border-b border-border bg-background/80 backdrop-blur-sm sticky top-0 z-10">
      <div className="max-w-5xl mx-auto px-6 py-3 flex items-center justify-between">
        <Link to={backTo} className="flex items-center gap-2 text-sm text-zinc-400 hover:text-zinc-300 transition">
          <ArrowLeft className="w-4 h-4" /> {backLabel}
        </Link>
        {action}
      </div>
    </div>
  )
}
