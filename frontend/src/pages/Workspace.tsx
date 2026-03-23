import { useState, useEffect, useRef } from 'react'
import { useParams } from 'react-router-dom'
import {
  Send, PanelRightClose, PanelRightOpen, CheckCircle2, Circle,
  Users, FileText, ListChecks, Inbox, Loader2, Folder,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { resolveIcon } from '@/lib/icons'
import {
  workspaces as wsApi,
  notifications as notifApi,
  type WorkspaceOut,
  type WorkspaceMessageOut,
  type WorkspaceTaskOut,
  type WorkspaceAgentOut,
  type NotificationOut,
} from '@/lib/api'

type RightTab = 'brief' | 'inbox' | 'tasks'

export function Workspace() {
  const { workspaceId } = useParams<{ workspaceId: string }>()
  const [ws, setWs] = useState<WorkspaceOut | null>(null)
  const [messages, setMessages] = useState<WorkspaceMessageOut[]>([])
  const [notifs, setNotifs] = useState<NotificationOut[]>([])
  const [loading, setLoading] = useState(true)
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [rightOpen, setRightOpen] = useState(true)
  const [rightTab, setRightTab] = useState<RightTab>('brief')
  const chatEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!workspaceId) return
    setLoading(true)
    Promise.all([
      wsApi.get(workspaceId),
      wsApi.listMessages(workspaceId),
      notifApi.list({ limit: 50 }),
    ]).then(([wsData, msgs, allNotifs]) => {
      setWs(wsData)
      setMessages(msgs)
      setNotifs(allNotifs.filter((n) => n.workspace_id === workspaceId))
    }).catch(() => {}).finally(() => setLoading(false))
  }, [workspaceId])

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const handleSend = async () => {
    if (!input.trim() || !workspaceId) return
    setSending(true)
    try {
      const msg = await wsApi.sendMessage(workspaceId, input.trim())
      setMessages((prev) => [...prev, msg])
      setInput('')
    } catch {}
    setSending(false)
  }

  if (loading || !ws) {
    return (
      <div className="animate-fade-in -m-8 h-screen flex items-center justify-center bg-[#050507]">
        <Loader2 className="w-5 h-5 text-zinc-500 animate-spin" />
      </div>
    )
  }

  const WsIcon = resolveIcon(ws.icon)
  const unreadNotifs = notifs.filter((n) => !n.is_read).length

  const statusColors: Record<string, string> = {
    open: 'bg-blue-400/10 text-blue-400 border-blue-400/20',
    in_progress: 'bg-amber-400/10 text-amber-400 border-amber-400/20',
    resolved: 'bg-emerald-400/10 text-emerald-400 border-emerald-400/20',
  }
  const statusLabels: Record<string, string> = { open: 'Open', in_progress: 'In Progress', resolved: 'Resolved' }

  return (
    <div className="animate-fade-in -m-8 h-screen flex flex-col bg-[#050507]">
      {/* Header */}
      <div className="shrink-0 flex items-center justify-between px-5 py-3 border-b border-white/[0.06]">
        <div className="flex items-center gap-3">
          <WsIcon className="w-5 h-5 text-zinc-400" />
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-[16px] font-semibold text-foreground">{ws.name}</h1>
              <span className={cn('text-[11px] px-2 py-0.5 rounded-full font-medium border', statusColors[ws.case_status] || statusColors.open)}>
                {statusLabels[ws.case_status] || 'Open'}
              </span>
            </div>
            <p className="text-[12px] text-zinc-500">{ws.agents.length} agents</p>
          </div>
        </div>
        <button onClick={() => setRightOpen(!rightOpen)} className="p-2 text-zinc-500 hover:text-white hover:bg-white/[0.06] rounded-lg transition-colors">
          {rightOpen ? <PanelRightClose className="w-4 h-4" /> : <PanelRightOpen className="w-4 h-4" />}
        </button>
      </div>

      <div className="flex-1 flex overflow-hidden min-h-0">
        {/* Chat */}
        <div className="flex-1 flex flex-col min-w-0">
          <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
            {messages.map((msg) => <ChatBubble key={msg.id} msg={msg} agents={ws.agents} />)}
            <div ref={chatEndRef} />
          </div>

          <div className="shrink-0 px-5 pb-4">
            <div className="flex items-center gap-2 bg-white/[0.04] border border-white/[0.08] rounded-xl px-4 py-2.5">
              <input
                className="flex-1 bg-transparent text-[14px] text-foreground placeholder-zinc-600 outline-none"
                placeholder="Message this workspace..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() } }}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || sending}
                className="p-1.5 rounded-lg text-zinc-500 hover:text-white hover:bg-white/[0.06] disabled:opacity-30 transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Right panel */}
        {rightOpen && (
          <div className="w-[340px] border-l border-white/[0.06] flex flex-col shrink-0 overflow-hidden">
            <div className="flex border-b border-white/[0.06]">
              {([
                { id: 'brief' as RightTab, label: 'Brief', icon: FileText },
                { id: 'inbox' as RightTab, label: 'Inbox', icon: Inbox, badge: unreadNotifs },
                { id: 'tasks' as RightTab, label: 'Tasks', icon: ListChecks },
              ]).map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setRightTab(tab.id)}
                  className={cn(
                    'flex-1 flex items-center justify-center gap-1.5 py-2.5 text-[12px] font-medium transition-colors relative',
                    rightTab === tab.id ? 'text-white' : 'text-zinc-500 hover:text-zinc-300'
                  )}
                >
                  <tab.icon className="w-3.5 h-3.5" />
                  {tab.label}
                  {tab.badge != null && tab.badge > 0 && (
                    <span className="text-[10px] px-1 rounded-full bg-red-500/20 text-red-400 font-medium">{tab.badge}</span>
                  )}
                  {rightTab === tab.id && <div className="absolute bottom-0 left-2 right-2 h-[2px] bg-white rounded-t-full" />}
                </button>
              ))}
            </div>

            <div className="flex-1 overflow-y-auto p-4">
              {rightTab === 'brief' && <BriefPanel ws={ws} />}
              {rightTab === 'inbox' && <InboxPanel items={notifs} />}
              {rightTab === 'tasks' && <TasksPanel tasks={ws.tasks} />}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function ChatBubble({ msg, agents }: { msg: WorkspaceMessageOut; agents: WorkspaceAgentOut[] }) {
  const isUser = msg.role === 'user'
  const isActivity = msg.role === 'activity'
  const AgentIcon = resolveIcon(msg.agent_icon)

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[70%] rounded-2xl rounded-br-md bg-white/[0.08] px-4 py-2.5">
          <p className="text-[14px] text-foreground leading-relaxed whitespace-pre-line">{msg.content}</p>
        </div>
      </div>
    )
  }

  return (
    <div className={cn('flex items-start gap-2.5', isActivity && 'opacity-80')}>
      <div className="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 mt-0.5" style={{ backgroundColor: msg.agent_color ? `${msg.agent_color}20` : 'rgba(255,255,255,0.08)' }}>
        <AgentIcon className="w-3.5 h-3.5" style={{ color: msg.agent_color || '#999' }} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-[11px] font-medium mb-1" style={{ color: msg.agent_color || '#999' }}>{msg.agent_name}</p>
        <div className={cn(
          'rounded-2xl rounded-tl-md px-4 py-2.5',
          isActivity ? 'bg-white/[0.03] border border-white/[0.06]' : 'bg-white/[0.04]'
        )}>
          <p className="text-[14px] text-zinc-300 leading-relaxed whitespace-pre-line">{msg.content}</p>
        </div>
      </div>
    </div>
  )
}

function BriefPanel({ ws }: { ws: WorkspaceOut }) {
  return (
    <div className="space-y-5">
      {ws.goal && (
        <div>
          <p className="text-[11px] uppercase tracking-wider text-zinc-500 font-medium mb-1.5">Goal</p>
          <p className="text-[13px] text-zinc-300 leading-relaxed">{ws.goal}</p>
        </div>
      )}
      {ws.brief && (
        <div>
          <p className="text-[11px] uppercase tracking-wider text-zinc-500 font-medium mb-1.5">Status</p>
          <p className="text-[13px] text-zinc-300 leading-relaxed">{ws.brief}</p>
        </div>
      )}
      {ws.progress != null && (
        <div>
          <p className="text-[11px] uppercase tracking-wider text-zinc-500 font-medium mb-1.5">Progress</p>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
              <div className="h-full bg-white/60 rounded-full" style={{ width: `${ws.progress}%` }} />
            </div>
            <span className="text-[12px] text-zinc-400 font-medium">{ws.progress}%</span>
          </div>
        </div>
      )}
      {ws.agents.length > 0 && (
        <div>
          <p className="text-[11px] uppercase tracking-wider text-zinc-500 font-medium mb-2">Agents</p>
          <div className="space-y-2">
            {ws.agents.map((wa) => {
              const Icon = resolveIcon(wa.agent_icon)
              return (
                <div key={wa.id} className="flex items-center gap-2.5 px-3 py-2 rounded-lg bg-white/[0.03]">
                  <div className="w-6 h-6 rounded flex items-center justify-center" style={{ backgroundColor: wa.agent_color ? `${wa.agent_color}20` : 'rgba(255,255,255,0.08)' }}>
                    <Icon className="w-3 h-3" style={{ color: wa.agent_color || '#999' }} />
                  </div>
                  <span className="text-[13px] text-zinc-300">{wa.agent_name}</span>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

function InboxPanel({ items }: { items: NotificationOut[] }) {
  if (items.length === 0) {
    return (
      <div className="text-center py-10">
        <Inbox className="w-6 h-6 text-zinc-700 mx-auto mb-2" />
        <p className="text-[13px] text-zinc-500">No notifications</p>
      </div>
    )
  }
  return (
    <div className="space-y-2">
      {items.map((item) => {
        const Icon = resolveIcon(item.agent_icon)
        return (
          <div key={item.id} className="px-3 py-2.5 rounded-lg bg-white/[0.03] border border-white/[0.04]">
            <div className="flex items-start gap-2">
              {!item.is_read && <Circle className="w-2 h-2 fill-blue-400 text-blue-400 shrink-0 mt-1.5" />}
              <div className="flex-1 min-w-0">
                <p className="text-[13px] font-medium text-foreground leading-snug">{item.title}</p>
                <p className="text-[12px] text-zinc-500 mt-0.5 line-clamp-2">{item.description}</p>
                <span className="text-[11px] font-medium mt-1 inline-block" style={{ color: item.agent_color || '#999' }}>{item.agent_name}</span>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

function TasksPanel({ tasks }: { tasks: WorkspaceTaskOut[] }) {
  const done = tasks.filter((t) => t.is_done)
  const pending = tasks.filter((t) => !t.is_done)

  return (
    <div className="space-y-4">
      <p className="text-[11px] uppercase tracking-wider text-zinc-500 font-medium">
        {done.length}/{tasks.length} completed
      </p>
      {pending.map((t) => (
        <div key={t.id} className="flex items-start gap-2.5">
          <Circle className="w-4 h-4 text-zinc-600 shrink-0 mt-0.5" />
          <div>
            <p className="text-[13px] text-foreground">{t.title}</p>
            {t.assignee_name && <p className="text-[11px] text-zinc-500 mt-0.5">{t.assignee_name}</p>}
          </div>
        </div>
      ))}
      {done.length > 0 && (
        <>
          <div className="border-t border-white/[0.06] pt-3">
            <p className="text-[11px] uppercase tracking-wider text-zinc-600 font-medium mb-2">Completed</p>
          </div>
          {done.map((t) => (
            <div key={t.id} className="flex items-start gap-2.5 opacity-50">
              <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
              <div>
                <p className="text-[13px] text-zinc-400 line-through">{t.title}</p>
                {t.assignee_name && <p className="text-[11px] text-zinc-600 mt-0.5">{t.assignee_name}</p>}
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  )
}
