import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { CheckCircle2, PlayCircle, FilePlus, Info, AlertCircle, ArrowRight, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { feed as feedApi, type FeedEventOut } from '@/lib/api'
import { resolveIcon } from '@/lib/icons'

const typeConfig: Record<string, { icon: typeof CheckCircle2; label: string; color: string }> = {
  task_complete: { icon: CheckCircle2, label: 'Task completed', color: '#34d399' },
  task_started: { icon: PlayCircle, label: 'Task started', color: '#60a5fa' },
  file_created: { icon: FilePlus, label: 'File created', color: '#a78bfa' },
  status_update: { icon: Info, label: 'Status update', color: '#fbbf24' },
  approval_request: { icon: AlertCircle, label: 'Needs approval', color: '#f87171' },
}

function relativeTime(dateStr: string): string {
  const now = Date.now()
  const then = new Date(dateStr).getTime()
  const diffMs = now - then
  const mins = Math.floor(diffMs / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

function isToday(dateStr: string): boolean {
  const d = new Date(dateStr)
  const now = new Date()
  return d.toDateString() === now.toDateString()
}

export function Feed() {
  const [items, setItems] = useState<FeedEventOut[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    feedApi.list().then(setItems).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const today = items.filter((i) => isToday(i.created_at))
  const earlier = items.filter((i) => !isToday(i.created_at))

  return (
    <div className="animate-fade-in -m-8 min-h-screen flex flex-col bg-[#050507]">
      <div className="flex-1 flex flex-col px-6 pt-10 pb-10">
        <div className="max-w-3xl mx-auto w-full">
          <h1 className="text-xl font-semibold text-foreground tracking-tight">Feed</h1>
          <p className="text-[13px] text-muted-foreground mt-0.5">Activity across your workspaces</p>

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-5 h-5 text-zinc-500 animate-spin" />
            </div>
          ) : items.length === 0 ? (
            <div className="text-center py-20">
              <p className="text-[14px] text-zinc-500">No activity yet</p>
            </div>
          ) : (
            <>
              {today.length > 0 && (
                <div className="mt-8">
                  <p className="text-[11px] uppercase tracking-wider text-zinc-500 font-medium mb-3 px-1">Today</p>
                  <div className="space-y-1">
                    {today.map((item) => <FeedRow key={item.id} item={item} />)}
                  </div>
                </div>
              )}
              {earlier.length > 0 && (
                <div className="mt-8">
                  <p className="text-[11px] uppercase tracking-wider text-zinc-500 font-medium mb-3 px-1">Earlier</p>
                  <div className="space-y-1">
                    {earlier.map((item) => <FeedRow key={item.id} item={item} />)}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

function FeedRow({ item }: { item: FeedEventOut }) {
  const cfg = typeConfig[item.event_type] ?? typeConfig.status_update
  const TypeIcon = cfg.icon
  const AgentIcon = resolveIcon(item.agent_icon)

  return (
    <Link
      to={`/workspaces/${item.workspace_id}`}
      className={cn(
        'flex items-start gap-3 px-4 py-3.5 rounded-xl transition-colors group',
        item.event_type === 'approval_request'
          ? 'bg-red-500/[0.04] hover:bg-red-500/[0.07] border border-red-500/[0.08]'
          : 'hover:bg-white/[0.03]'
      )}
    >
      <div
        className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0 mt-0.5"
        style={{ backgroundColor: item.agent_color ? `${item.agent_color}15` : 'rgba(255,255,255,0.06)' }}
      >
        <AgentIcon className="w-4 h-4" style={{ color: item.agent_color || '#999' }} />
      </div>

      <div className="flex-1 min-w-0">
        <span className="text-[14px] font-medium text-foreground leading-snug">{item.title}</span>
        <p className="text-[13px] text-zinc-400 mt-0.5 leading-relaxed">{item.description}</p>
        <div className="flex items-center gap-2 mt-2">
          <div className="flex items-center gap-1">
            <TypeIcon className="w-3 h-3" style={{ color: cfg.color }} />
            <span className="text-[11px] font-medium" style={{ color: cfg.color }}>{cfg.label}</span>
          </div>
          <span className="text-zinc-700 text-[11px]">·</span>
          <span className="text-[11px] text-zinc-500">{item.agent_name}</span>
          <span className="text-zinc-700 text-[11px]">·</span>
          <span className="text-[11px] text-zinc-600">{item.workspace_name}</span>
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0 pt-1">
        <span className="text-[12px] text-zinc-600">{relativeTime(item.created_at)}</span>
        <ArrowRight className="w-3.5 h-3.5 text-zinc-700 opacity-0 group-hover:opacity-100 transition-opacity" />
      </div>
    </Link>
  )
}
