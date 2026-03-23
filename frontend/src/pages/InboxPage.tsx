import { useState, useEffect } from 'react'
import { Inbox, Circle, ArrowRight, Loader2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { cn } from '@/lib/utils'
import { notifications as notifApi, type NotificationOut } from '@/lib/api'
import { resolveIcon } from '@/lib/icons'

type FilterTab = 'all' | 'approval' | 'report'

const tabs: { id: FilterTab; label: string }[] = [
  { id: 'all', label: 'All' },
  { id: 'approval', label: 'Approvals' },
  { id: 'report', label: 'Reports' },
]

export function InboxPage() {
  const [allItems, setAllItems] = useState<NotificationOut[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<FilterTab>('all')
  const [selectedId, setSelectedId] = useState<string | null>(null)

  useEffect(() => {
    notifApi.list({ limit: 200 })
      .then((items) => {
        setAllItems(items)
        if (items.length > 0) setSelectedId(items[0].id)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const filtered = activeTab === 'all' ? allItems : allItems.filter((item) => item.notification_type === activeTab)
  const selected = allItems.find((item) => item.id === selectedId) ?? null
  const unreadCount = allItems.filter((i) => !i.is_read).length
  const approvalCount = allItems.filter((i) => i.notification_type === 'approval').length
  const reportCount = allItems.filter((i) => i.notification_type === 'report').length
  const tabCounts: Record<FilterTab, number> = { all: allItems.length, approval: approvalCount, report: reportCount }

  if (loading) {
    return (
      <div className="animate-fade-in -m-8 h-screen flex items-center justify-center bg-[#050507]">
        <Loader2 className="w-5 h-5 text-zinc-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="animate-fade-in -m-8 h-screen flex flex-col bg-[#050507]">
      <div className="shrink-0 px-6 pt-8 pb-0">
        <h1 className="text-xl font-semibold text-foreground tracking-tight">Notifications</h1>
        <p className="text-[13px] text-muted-foreground mt-0.5">{unreadCount} unread · {allItems.length} total from your agents</p>

        <div className="flex gap-1 mt-4 border-b border-white/[0.06]">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setActiveTab(tab.id)
                const first = tab.id === 'all' ? allItems[0] : allItems.find((i) => i.notification_type === tab.id)
                if (first) setSelectedId(first.id)
              }}
              className={cn(
                'flex items-center gap-1.5 px-4 py-2.5 text-[13px] font-medium transition-colors relative',
                activeTab === tab.id ? 'text-white' : 'text-zinc-500 hover:text-zinc-300'
              )}
            >
              {tab.label}
              <span className={cn('text-[12px]', activeTab === tab.id ? 'text-zinc-300' : 'text-zinc-600')}>{tabCounts[tab.id]}</span>
              {activeTab === tab.id && <div className="absolute bottom-0 left-2 right-2 h-[2px] bg-white rounded-t-full" />}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden min-h-0">
        <div className="w-[340px] border-r border-white/[0.06] overflow-y-auto shrink-0">
          {filtered.length === 0 ? (
            <div className="text-center py-16">
              <Inbox className="w-8 h-8 text-zinc-700 mx-auto mb-2" />
              <p className="text-[13px] text-zinc-500">No items</p>
            </div>
          ) : (
            filtered.map((item) => {
              const AgentIcon = resolveIcon(item.agent_icon)
              const isSelected = item.id === selectedId
              return (
                <button
                  key={item.id}
                  onClick={() => setSelectedId(item.id)}
                  className={cn(
                    'w-full text-left px-5 py-4 border-b border-white/[0.04] transition-colors',
                    isSelected ? 'bg-white/[0.06]' : 'hover:bg-white/[0.03]'
                  )}
                >
                  <div className="flex items-start gap-2.5">
                    {!item.is_read ? <Circle className="w-2 h-2 fill-blue-400 text-blue-400 shrink-0 mt-2" /> : <div className="w-2 shrink-0" />}
                    <div className="flex-1 min-w-0">
                      <p className={cn('text-[14px] leading-snug truncate', item.is_read ? 'text-zinc-300 font-normal' : 'text-foreground font-medium')}>{item.title}</p>
                      <p className="text-[12px] text-zinc-500 mt-1 line-clamp-2 leading-relaxed">{item.description}</p>
                      <div className="flex items-center gap-1.5 mt-2">
                        <span className="text-[11px] font-medium" style={{ color: item.agent_color || '#999' }}>{item.agent_name}</span>
                        <span className="text-zinc-700 text-[11px]">·</span>
                        <span className="text-[11px] text-zinc-600">{item.workspace_name}</span>
                        <span className="text-zinc-700 text-[11px]">·</span>
                        <PriorityBadge priority={item.priority} />
                      </div>
                    </div>
                  </div>
                </button>
              )
            })
          )}
        </div>

        <div className="flex-1 overflow-y-auto">
          {selected ? <DetailView item={selected} /> : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Inbox className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
                <p className="text-[14px] text-zinc-500">Select an item to view details</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function DetailView({ item }: { item: NotificationOut }) {
  const AgentIcon = resolveIcon(item.agent_icon)
  const actions = Array.isArray(item.action_buttons) ? item.action_buttons as { label: string; variant: string }[] : []

  return (
    <div className="max-w-2xl px-8 py-8">
      <div className="flex items-center gap-2 mb-4">
        <span className={cn(
          'text-[11px] px-2 py-0.5 rounded font-medium border',
          item.notification_type === 'approval' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 'bg-blue-500/10 text-blue-400 border-blue-500/20'
        )}>
          {item.notification_type === 'approval' ? 'Approval Request' : 'Completion Report'}
        </span>
        <PriorityTag priority={item.priority} />
      </div>

      <h2 className="text-lg font-semibold text-foreground">{item.title}</h2>

      <div className="flex items-center gap-2 mt-2 mb-6">
        <div className="flex items-center gap-1.5">
          <div className="w-5 h-5 rounded flex items-center justify-center" style={{ backgroundColor: item.agent_color ? `${item.agent_color}20` : 'rgba(255,255,255,0.08)' }}>
            <AgentIcon className="w-3 h-3" style={{ color: item.agent_color || '#999' }} />
          </div>
          <span className="text-[13px] font-medium" style={{ color: item.agent_color || '#999' }}>{item.agent_name}</span>
        </div>
        <span className="text-zinc-700">·</span>
        <span className="text-[13px] text-zinc-500">{item.workspace_name}</span>
      </div>

      <div className="rounded-xl bg-white/[0.03] border border-white/[0.06] p-5 mb-6">
        <div className="flex items-start gap-3">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 mt-0.5" style={{ backgroundColor: item.agent_color ? `${item.agent_color}20` : 'rgba(255,255,255,0.08)' }}>
            <AgentIcon className="w-3.5 h-3.5" style={{ color: item.agent_color || '#999' }} />
          </div>
          <div className="text-[14px] text-zinc-300 leading-relaxed whitespace-pre-line">{item.detail}</div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {actions.map((action) => (
          <button
            key={action.label}
            className={cn(
              'px-4 py-2 rounded-lg text-[14px] font-medium transition-colors flex items-center gap-2',
              action.variant === 'primary' ? 'bg-white text-black hover:bg-zinc-200' : 'bg-white/[0.06] text-zinc-300 hover:bg-white/[0.1] border border-white/[0.08]'
            )}
          >
            {action.label}
          </button>
        ))}
        {item.workspace_id && (
          <Link to={`/workspaces/${item.workspace_id}`} className="px-4 py-2 rounded-lg text-[14px] font-medium text-zinc-400 hover:text-zinc-200 transition-colors flex items-center gap-1.5">
            Open Workspace <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        )}
      </div>
    </div>
  )
}

function PriorityBadge({ priority }: { priority: string }) {
  const colors: Record<string, string> = { high: 'text-red-400', medium: 'text-amber-400', low: 'text-zinc-500' }
  return <span className={cn('text-[11px] font-medium', colors[priority] || 'text-zinc-500')}>{priority}</span>
}

function PriorityTag({ priority }: { priority: string }) {
  const styles: Record<string, string> = {
    high: 'bg-red-500/10 text-red-400 border-red-500/20',
    medium: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    low: 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20',
  }
  return <span className={cn('text-[11px] px-2 py-0.5 rounded font-medium border capitalize', styles[priority] || styles.low)}>{priority} Priority</span>
}
