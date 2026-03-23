import { useState, useRef, useEffect } from 'react'
import { Bell, ArrowRight, Circle } from 'lucide-react'
import { Link } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { notifications as notifApi, type NotificationOut } from '@/lib/api'
import { resolveIcon } from '@/lib/icons'

export function NotificationBell() {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const [items, setItems] = useState<NotificationOut[]>([])
  const [count, setCount] = useState(0)

  useEffect(() => {
    notifApi.unreadCount().then((r) => setCount(r.unread_count)).catch(() => {})
    notifApi.list({ unread_only: true, limit: 8 }).then(setItems).catch(() => {})
  }, [])

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(!open)}
        className={cn(
          'relative p-2 rounded-lg transition-colors',
          open ? 'bg-white/[0.08] text-white' : 'text-zinc-400 hover:text-white hover:bg-white/[0.06]'
        )}
      >
        <Bell className="w-[18px] h-[18px]" />
        {count > 0 && (
          <span className="absolute -top-0.5 -right-0.5 flex items-center justify-center w-4.5 h-4.5 min-w-[18px] px-1 rounded-full bg-red-500 text-white text-[10px] font-bold leading-none">
            {count}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-[380px] rounded-xl border border-white/[0.08] bg-[#0c0c10] shadow-2xl shadow-black/50 z-50 overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-white/[0.06]">
            <div className="flex items-center gap-2">
              <p className="text-[14px] font-semibold text-foreground">Notifications</p>
              {count > 0 && (
                <span className="text-[11px] px-1.5 py-0.5 rounded-full bg-red-500/20 text-red-400 font-medium">{count}</span>
              )}
            </div>
            <Link to="/notifications" onClick={() => setOpen(false)} className="text-[12px] text-zinc-400 hover:text-white transition-colors flex items-center gap-1">
              See all <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="max-h-[400px] overflow-y-auto">
            {items.length === 0 ? (
              <div className="py-10 text-center">
                <Bell className="w-8 h-8 text-zinc-700 mx-auto mb-2" />
                <p className="text-[13px] text-zinc-500">You're all caught up</p>
              </div>
            ) : (
              items.map((item) => {
                const AgentIcon = resolveIcon(item.agent_icon)
                return (
                  <Link
                    key={item.id}
                    to={item.workspace_id ? `/workspaces/${item.workspace_id}` : '/notifications'}
                    onClick={() => setOpen(false)}
                    className="flex items-start gap-3 px-4 py-3.5 hover:bg-white/[0.04] transition-colors border-b border-white/[0.04] last:border-b-0"
                  >
                    <div className="relative shrink-0 mt-0.5">
                      <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: item.agent_color ? `${item.agent_color}20` : 'rgba(255,255,255,0.08)' }}>
                        <AgentIcon className="w-4 h-4" style={{ color: item.agent_color || '#999' }} />
                      </div>
                      {!item.is_read && <Circle className="absolute -top-0.5 -left-0.5 w-2.5 h-2.5 fill-blue-400 text-blue-400" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-[13px] font-medium text-foreground leading-snug">{item.title}</p>
                      <p className="text-[12px] text-zinc-500 mt-0.5 line-clamp-1">{item.description}</p>
                      <div className="flex items-center gap-1.5 mt-1.5">
                        <span className="text-[11px]" style={{ color: item.agent_color || '#999' }}>{item.agent_name}</span>
                        <span className="text-zinc-700 text-[11px]">·</span>
                        <span className="text-[11px] text-zinc-600">{item.workspace_name}</span>
                      </div>
                    </div>
                    <PriorityDot priority={item.priority} />
                  </Link>
                )
              })
            )}
          </div>

          {items.length > 0 && (
            <div className="border-t border-white/[0.06] px-4 py-2.5">
              <Link to="/notifications" onClick={() => setOpen(false)} className="text-[12px] text-zinc-400 hover:text-white transition-colors flex items-center justify-center gap-1">
                View all notifications <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function PriorityDot({ priority }: { priority: string }) {
  const colors: Record<string, string> = { high: 'bg-red-400', medium: 'bg-amber-400', low: 'bg-zinc-500' }
  return <div className={cn('w-2 h-2 rounded-full shrink-0 mt-2', colors[priority] || 'bg-zinc-500')} title={`${priority} priority`} />
}
