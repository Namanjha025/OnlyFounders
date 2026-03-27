import { useState, useEffect, useRef } from 'react'
import { useParams, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom'
import {
  Send, CheckCircle2, Circle, ListChecks, Bell,
  Loader2, ChevronDown, Users, Plus, MoreHorizontal, ArrowLeft,
  ChevronRight, X, Home, Clock, Search,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { resolveIcon } from '@/lib/icons'
import {
  workspaces as wsApi,
  notifications as notifApi,
  agents as agentsApi,
  team as teamApi,
  type WorkspaceOut,
  type WorkspaceMessageOut,
  type WorkspaceTaskOut,
  type WorkspaceAgentOut,
  type NotificationOut,
  type CaseStatus,
  type AgentOut,
} from '@/lib/api'

export function Workspace() {
  const { workspaceId } = useParams<{ workspaceId: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const [ws, setWs] = useState<WorkspaceOut | null>(null)
  const [messages, setMessages] = useState<WorkspaceMessageOut[]>([])
  const [notifs, setNotifs] = useState<NotificationOut[]>([])
  const [loading, setLoading] = useState(true)
  const [statusOpen, setStatusOpen] = useState(false)
  const [panelOpen, setPanelOpen] = useState(false)

  const basePath = `/cases/${workspaceId}`
  const currentSub = location.pathname.replace(basePath, '').replace(/^\//, '') || 'chat'
  const isOnHome = currentSub === 'chat' || currentSub === ''

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

  if (loading || !ws) {
    return (
      <div className="animate-fade-in flex-1 flex items-center justify-center bg-[#0a0a0c]">
        <Loader2 className="w-5 h-5 text-zinc-500 animate-spin" />
      </div>
    )
  }

  const WsIcon = resolveIcon(ws.icon)
  const unreadNotifs = notifs.filter((n) => !n.is_read).length
  const doneTasks = ws.tasks.filter((t) => t.is_done)

  const statusColors: Record<string, string> = {
    open: 'bg-blue-500/15 text-blue-400 border-blue-500/25',
    in_progress: 'bg-amber-500/15 text-amber-400 border-amber-500/25',
    resolved: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/25',
  }
  const statusLabels: Record<string, string> = { open: 'Open', in_progress: 'In Progress', resolved: 'Resolved' }
  const allStatuses: CaseStatus[] = ['open', 'in_progress', 'resolved']

  const handleStatusChange = async (newStatus: CaseStatus) => {
    setStatusOpen(false)
    if (newStatus === ws.case_status || !workspaceId) return
    try {
      const updated = await wsApi.update(workspaceId, { case_status: newStatus })
      setWs(updated)
    } catch {}
  }

  const navigateTo = (sub: string) => {
    setPanelOpen(false)
    navigate(`${basePath}/${sub}`)
  }

  const PANEL_NAV = [
    { key: 'chat', icon: Home, label: 'Home' },
    { key: 'history', icon: Clock, label: 'History', sub: `${messages.length} messages` },
    { key: 'agents', icon: Users, label: 'Agents', sub: `${ws.agents.length} assigned` },
    { key: 'tasks', icon: ListChecks, label: 'Tasks', sub: `${doneTasks.length}/${ws.tasks.length} done` },
    { key: 'notifications', icon: Bell, label: 'Notifications', sub: unreadNotifs > 0 ? `${unreadNotifs} unread` : 'All caught up' },
  ]

  return (
    <div className="animate-fade-in flex-1 flex flex-col bg-[#0a0a0c] overflow-hidden">
      {/* Header — minimal, no border */}
      <div className="shrink-0 flex items-center justify-between px-5 h-12">
        <div className="flex items-center gap-2.5">
          {!isOnHome && (
            <button
              onClick={() => navigate(`${basePath}/chat`)}
              className="p-1.5 -ml-1 text-zinc-500 hover:text-white hover:bg-white/[0.06] rounded-lg transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
          )}
          <h1 className="text-[15px] font-semibold text-foreground">{ws.name}</h1>
          <div className="relative">
            <button
              onClick={() => setStatusOpen(!statusOpen)}
              className={cn('text-[10px] px-2 py-0.5 rounded-full font-semibold border flex items-center gap-1 transition-colors hover:brightness-125', statusColors[ws.case_status] || statusColors.open)}
            >
              {statusLabels[ws.case_status] || 'Open'}
              <ChevronDown className="w-2.5 h-2.5" />
            </button>
            {statusOpen && (
              <>
                <div className="fixed inset-0 z-40" onClick={() => setStatusOpen(false)} />
                <div className="absolute top-full left-0 mt-1.5 z-50 bg-[#161619] border border-white/[0.08] rounded-xl shadow-2xl py-1.5 min-w-[150px]">
                  {allStatuses.map((s) => (
                    <button
                      key={s}
                      onClick={() => handleStatusChange(s)}
                      className={cn(
                        'w-full text-left px-3 py-2 text-[13px] font-medium transition-colors flex items-center gap-2.5',
                        s === ws.case_status ? 'text-white bg-white/[0.06]' : 'text-zinc-400 hover:text-white hover:bg-white/[0.04]'
                      )}
                    >
                      <div className={cn('w-2 h-2 rounded-full', s === 'open' ? 'bg-blue-400' : s === 'in_progress' ? 'bg-amber-400' : 'bg-emerald-400')} />
                      {statusLabels[s]}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>

        <button
          onClick={() => setPanelOpen(!panelOpen)}
          className={cn(
            'w-9 h-9 rounded-xl flex items-center justify-center transition-colors',
            panelOpen ? 'bg-white/[0.1] text-white' : 'text-zinc-500 hover:text-white hover:bg-white/[0.06]'
          )}
        >
          <MoreHorizontal className="w-5 h-5" />
        </button>
      </div>

      {/* Body */}
      <div className="flex-1 flex overflow-hidden min-h-0">
        <div className="flex-1 min-w-0 flex flex-col">
          <Routes>
            <Route index element={<Navigate to="chat" replace />} />
            <Route path="chat" element={
              <ChatView workspaceId={workspaceId!} ws={ws} messages={messages} setMessages={setMessages} />
            } />
            <Route path="history" element={<HistoryView messages={messages} ws={ws} />} />
            <Route path="agents" element={<AgentsView ws={ws} workspaceId={workspaceId!} setWs={setWs} />} />
            <Route path="tasks" element={<TasksView ws={ws} workspaceId={workspaceId!} setWs={setWs} />} />
            <Route path="notifications" element={<NotificationsView notifs={notifs} />} />
          </Routes>
        </div>

        {/* Right panel */}
        {panelOpen && (
          <>
            <div className="fixed inset-0 z-30 bg-black/30" onClick={() => setPanelOpen(false)} />
            <div className="relative z-40 w-[280px] shrink-0 bg-[#111114] flex flex-col animate-slide-in-right">
              <div className="px-5 pt-5 pb-4">
                <div className="flex items-center justify-between mb-2">
                  <h2 className="text-[15px] font-semibold text-foreground">{ws.name}</h2>
                  <button onClick={() => setPanelOpen(false)} className="p-1.5 text-zinc-600 hover:text-white rounded-lg hover:bg-white/[0.06] transition-colors">
                    <X className="w-4 h-4" />
                  </button>
                </div>
                <p className="text-[12px] text-zinc-600">{ws.agents.length} agents</p>
              </div>

              <div className="flex-1 overflow-y-auto py-1 px-2">
                {PANEL_NAV.map(({ key, icon: Icon, label, sub }) => {
                  const active = key === 'chat' ? isOnHome : currentSub === key
                  return (
                    <button
                      key={key}
                      onClick={() => navigateTo(key)}
                      className={cn(
                        'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-colors text-left group',
                        active ? 'bg-white/[0.06] text-white' : 'text-zinc-400 hover:bg-white/[0.04] hover:text-zinc-200'
                      )}
                    >
                      <div className="relative">
                        <Icon className="w-[18px] h-[18px]" />
                        {key === 'notifications' && unreadNotifs > 0 && (
                          <div className="absolute -top-0.5 -right-0.5 w-2 h-2 rounded-full bg-blue-400" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-[14px] font-medium">{label}</p>
                        {sub && <p className="text-[12px] text-zinc-600 mt-0.5">{sub}</p>}
                      </div>
                      <ChevronRight className="w-4 h-4 text-zinc-700 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                    </button>
                  )
                })}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

/* ─── Chat / Home View ───────────────────────────────────────── */

function ChatView({
  workspaceId, ws, messages, setMessages,
}: {
  workspaceId: string
  ws: WorkspaceOut
  messages: WorkspaceMessageOut[]
  setMessages: React.Dispatch<React.SetStateAction<WorkspaceMessageOut[]>>
}) {
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const chatEndRef = useRef<HTMLDivElement>(null)
  const WsIcon = resolveIcon(ws.icon)

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const handleSend = async () => {
    if (!input.trim()) return
    const text = input.trim()
    setInput('')
    setSending(true)
    try {
      const msg = await wsApi.sendMessage(workspaceId, text)
      setMessages((prev) => [...prev, msg])
    } catch {}
    setSending(false)
  }

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Pinned hero */}
      <div className="shrink-0 flex flex-col items-center text-center py-6">
        <div className="w-12 h-12 rounded-2xl bg-white/[0.06] flex items-center justify-center mb-2">
          <WsIcon className="w-6 h-6 text-zinc-300" />
        </div>
        <h2 className="text-[17px] font-bold text-foreground tracking-tight">{ws.name}</h2>
        {ws.goal && (
          <p className="text-[13px] text-zinc-500 max-w-sm leading-relaxed mt-1">{ws.goal}</p>
        )}
      </div>

      {/* Scrollable messages only */}
      <div className="flex-1 overflow-y-auto min-h-0">
        <div className="max-w-[720px] mx-auto px-6 space-y-5 pb-4">
          {messages.length === 0 && (
            <p className="text-center text-zinc-600 text-[13px] pt-6">No messages yet. Start the conversation below.</p>
          )}
          {messages.map((msg) => <ChatBubble key={msg.id} msg={msg} />)}
          <div ref={chatEndRef} />
        </div>
      </div>

      {/* Pinned input */}
      <div className="shrink-0 pb-5 pt-2 px-6">
        <div className="max-w-[720px] mx-auto">
          <div className="relative flex items-end bg-white/[0.04] rounded-2xl transition-colors focus-within:bg-white/[0.06]">
            <input
              className="flex-1 bg-transparent text-[15px] text-foreground placeholder-zinc-600 outline-none px-5 py-4 min-h-[52px]"
              placeholder={`Message ${ws.name}...`}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() } }}
            />
            <div className="flex items-center gap-1 pr-3 pb-3">
              <button
                onClick={handleSend}
                disabled={!input.trim() || sending}
                className={cn(
                  'w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-200',
                  input.trim()
                    ? 'bg-white text-black hover:bg-zinc-200'
                    : 'bg-white/[0.06] text-zinc-600 cursor-default'
                )}
              >
                <Send className="w-[18px] h-[18px]" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

/* ─── History View ───────────────────────────────────────────── */

function HistoryView({ messages, ws }: { messages: WorkspaceMessageOut[]; ws: WorkspaceOut }) {
  const grouped = groupMessagesByDate(messages)

  return (
    <div className="flex-1 overflow-y-auto p-8 max-w-2xl">
      <h2 className="text-[18px] font-semibold text-foreground mb-1">History</h2>
      <p className="text-[13px] text-zinc-600 mb-6">{messages.length} messages in this case</p>

      {messages.length === 0 ? (
        <div className="text-center pt-12">
          <Clock className="w-8 h-8 text-zinc-700 mx-auto mb-3" />
          <p className="text-[15px] text-zinc-600">No messages yet</p>
        </div>
      ) : (
        <div className="space-y-6">
          {grouped.map(({ label, msgs }) => (
            <div key={label}>
              <p className="text-[11px] uppercase tracking-wider text-zinc-600 font-medium mb-3 px-1">{label}</p>
              <div className="space-y-1">
                {msgs.map((msg) => {
                  const AgentIcon = resolveIcon(msg.agent_icon)
                  const isUser = msg.role === 'user'
                  return (
                    <div key={msg.id} className="flex items-start gap-3 px-3 py-2.5 rounded-xl hover:bg-white/[0.03] transition-colors">
                      {isUser ? (
                        <div className="w-7 h-7 rounded-full bg-white/[0.08] flex items-center justify-center shrink-0 mt-0.5">
                          <span className="text-[10px] font-bold text-zinc-400">You</span>
                        </div>
                      ) : (
                        <div
                          className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5"
                          style={{ backgroundColor: msg.agent_color ? `${msg.agent_color}20` : 'rgba(255,255,255,0.08)' }}
                        >
                          <AgentIcon className="w-3.5 h-3.5" style={{ color: msg.agent_color || '#999' }} />
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-[13px] font-medium text-zinc-300">
                            {isUser ? 'You' : msg.agent_name}
                          </span>
                          <span className="text-[11px] text-zinc-700">
                            {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                        <p className="text-[13px] text-zinc-500 mt-0.5 line-clamp-2">{msg.content}</p>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function groupMessagesByDate(messages: WorkspaceMessageOut[]) {
  const groups: { label: string; msgs: WorkspaceMessageOut[] }[] = []
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)

  for (const msg of messages) {
    const d = new Date(msg.created_at)
    let label: string
    if (d.toDateString() === today.toDateString()) label = 'Today'
    else if (d.toDateString() === yesterday.toDateString()) label = 'Yesterday'
    else label = d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })

    const last = groups[groups.length - 1]
    if (last && last.label === label) {
      last.msgs.push(msg)
    } else {
      groups.push({ label, msgs: [msg] })
    }
  }
  return groups
}

/* ─── Agents View ────────────────────────────────────────────── */

function AgentsView({
  ws, workspaceId, setWs,
}: {
  ws: WorkspaceOut
  workspaceId: string
  setWs: React.Dispatch<React.SetStateAction<WorkspaceOut | null>>
}) {
  const [showAdd, setShowAdd] = useState(false)
  const [catalog, setCatalog] = useState<AgentOut[]>([])
  const [catalogLoading, setCatalogLoading] = useState(false)
  const [search, setSearch] = useState('')
  const [adding, setAdding] = useState<Set<string>>(new Set())

  const assignedIds = new Set(ws.agents.map((a) => a.agent_id))

  const loadCatalog = async () => {
    if (catalog.length > 0) { setShowAdd(true); return }
    setCatalogLoading(true)
    try {
      const agents = await agentsApi.list()
      setCatalog(agents)
    } catch {}
    setCatalogLoading(false)
    setShowAdd(true)
  }

  const handleAdd = async (agent: AgentOut) => {
    if (adding.has(agent.id)) return
    setAdding((p) => new Set(p).add(agent.id))
    try {
      const wa = await wsApi.addAgent(workspaceId, agent.id)
      setWs((prev) => prev ? { ...prev, agents: [...prev.agents, wa] } : prev)
      try { await teamApi.hire({ agent_id: agent.id }) } catch { /* already on team */ }
    } catch {}
    setAdding((p) => { const n = new Set(p); n.delete(agent.id); return n })
  }

  const handleRemove = async (agentId: string) => {
    try {
      await wsApi.removeAgent(workspaceId, agentId)
      setWs((prev) => prev ? { ...prev, agents: prev.agents.filter((a) => a.agent_id !== agentId) } : prev)
    } catch {}
  }

  const query = search.toLowerCase().trim()
  const available = catalog.filter((a) =>
    !assignedIds.has(a.id) &&
    (!query || a.name.toLowerCase().includes(query) || (a.category || '').toLowerCase().includes(query))
  )

  return (
    <div className="flex-1 overflow-y-auto p-8 max-w-2xl">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-[18px] font-semibold text-foreground">Agents ({ws.agents.length})</h2>
        <button
          onClick={loadCatalog}
          disabled={catalogLoading}
          className="flex items-center gap-1.5 text-[13px] font-medium text-zinc-400 hover:text-white px-3 py-1.5 rounded-lg hover:bg-white/[0.06] transition-colors"
        >
          {catalogLoading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Plus className="w-3.5 h-3.5" />}
          Add Agent
        </button>
      </div>

      {/* Add-agent browser */}
      {showAdd && (
        <div className="mb-6 rounded-xl border border-white/[0.08] bg-white/[0.02] p-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-[13px] font-medium text-zinc-300">Browse agents to add</p>
            <button onClick={() => { setShowAdd(false); setSearch('') }} className="p-1 text-zinc-600 hover:text-white rounded transition-colors">
              <X className="w-4 h-4" />
            </button>
          </div>
          <div className="relative mb-3">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-600" />
            <input
              className="w-full pl-8 pr-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08] text-[13px] text-foreground placeholder-zinc-600 outline-none focus:border-white/[0.16] transition-colors"
              placeholder="Search agents..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              autoFocus
            />
          </div>
          {available.length === 0 ? (
            <p className="text-[13px] text-zinc-600 text-center py-4">
              {query ? 'No matching agents found.' : 'All agents are already assigned.'}
            </p>
          ) : (
            <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto">
              {available.map((agent) => {
                const AgentIcon = resolveIcon(agent.icon)
                const isAdding = adding.has(agent.id)
                return (
                  <button
                    key={agent.id}
                    onClick={() => handleAdd(agent)}
                    disabled={isAdding}
                    className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg border border-white/[0.06] bg-white/[0.02] text-zinc-400 hover:bg-white/[0.06] hover:text-white transition-colors text-left disabled:opacity-50"
                  >
                    <div
                      className="w-7 h-7 rounded-md flex items-center justify-center shrink-0"
                      style={{ backgroundColor: agent.color ? `${agent.color}15` : 'rgba(255,255,255,0.06)' }}
                    >
                      <AgentIcon className="w-3.5 h-3.5" style={{ color: agent.color || '#999' }} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-[13px] font-medium truncate">{agent.name}</p>
                      <p className="text-[11px] text-zinc-600 truncate">{agent.category || 'General'}</p>
                    </div>
                    {isAdding ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin shrink-0" />
                    ) : (
                      <Plus className="w-3.5 h-3.5 shrink-0 text-zinc-600" />
                    )}
                  </button>
                )
              })}
            </div>
          )}
        </div>
      )}

      {/* Assigned agents */}
      {ws.agents.length === 0 ? (
        <p className="text-[15px] text-zinc-600 italic">No agents assigned to this case.</p>
      ) : (
        <div className="space-y-1">
          {ws.agents.map((wa) => {
            const Icon = resolveIcon(wa.agent_icon)
            return (
              <div key={wa.id} className="flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-white/[0.03] transition-colors group">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
                  style={{ backgroundColor: wa.agent_color ? `${wa.agent_color}15` : 'rgba(255,255,255,0.06)' }}
                >
                  <Icon className="w-5 h-5" style={{ color: wa.agent_color || '#999' }} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[15px] text-zinc-200 font-medium truncate">{wa.agent_name}</p>
                  {wa.agent_description && (
                    <p className="text-[13px] text-zinc-500 mt-0.5 line-clamp-1">{wa.agent_description}</p>
                  )}
                  {wa.agent_category && (
                    <span className="text-[11px] text-zinc-600 bg-white/[0.04] px-2 py-0.5 rounded-full mt-1 inline-block">{wa.agent_category}</span>
                  )}
                </div>
                <button
                  onClick={() => handleRemove(wa.agent_id)}
                  className="text-[12px] text-zinc-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all px-2 py-1 rounded-md hover:bg-red-400/10"
                >
                  Remove
                </button>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

/* ─── Tasks View ─────────────────────────────────────────────── */

function TasksView({
  ws, workspaceId, setWs,
}: {
  ws: WorkspaceOut
  workspaceId: string
  setWs: React.Dispatch<React.SetStateAction<WorkspaceOut | null>>
}) {
  const [newTitle, setNewTitle] = useState('')
  const [adding, setAdding] = useState(false)
  const pending = ws.tasks.filter((t) => !t.is_done)
  const done = ws.tasks.filter((t) => t.is_done)

  const handleAdd = async () => {
    if (!newTitle.trim()) return
    setAdding(true)
    try {
      const task = await wsApi.createTask(workspaceId, { title: newTitle.trim() })
      setWs((prev) => prev ? { ...prev, tasks: [...prev.tasks, task] } : prev)
      setNewTitle('')
    } catch {}
    setAdding(false)
  }

  const handleToggle = async (task: WorkspaceTaskOut) => {
    try {
      const updated = await wsApi.updateTask(workspaceId, task.id, { is_done: !task.is_done })
      setWs((prev) => prev ? { ...prev, tasks: prev.tasks.map((t) => t.id === updated.id ? updated : t) } : prev)
    } catch {}
  }

  return (
    <div className="flex-1 overflow-y-auto p-8 max-w-2xl">
      <h2 className="text-[18px] font-semibold text-foreground mb-6">
        Tasks <span className="text-zinc-500 font-normal text-[15px]">({done.length}/{ws.tasks.length} done)</span>
      </h2>

      <div className="flex items-center gap-2 mb-6">
        <div className="flex-1 flex items-center gap-2 bg-white/[0.04] border border-white/[0.08] rounded-xl px-4 py-2.5">
          <Plus className="w-4 h-4 text-zinc-600 shrink-0" />
          <input
            className="flex-1 bg-transparent text-[14px] text-foreground placeholder-zinc-600 outline-none"
            placeholder="Add a task..."
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAdd() } }}
          />
        </div>
        <button
          onClick={handleAdd}
          disabled={!newTitle.trim() || adding}
          className="text-[13px] px-4 py-2.5 rounded-xl bg-white/[0.08] text-zinc-300 hover:bg-white/[0.12] disabled:opacity-30 transition-colors font-medium"
        >
          Add
        </button>
      </div>

      {pending.length > 0 && (
        <div className="mb-6">
          <p className="text-[11px] uppercase tracking-wider text-zinc-500 font-medium mb-2 px-1">Pending</p>
          <div className="space-y-0.5">
            {pending.map((t) => (
              <button
                key={t.id}
                onClick={() => handleToggle(t)}
                className="w-full flex items-start gap-3 px-3 py-3 rounded-xl hover:bg-white/[0.03] transition-colors text-left"
              >
                <Circle className="w-[18px] h-[18px] text-zinc-600 shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-[15px] text-zinc-300">{t.title}</p>
                  {t.assignee_name && <p className="text-[12px] text-zinc-600 mt-0.5">{t.assignee_name}</p>}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {done.length > 0 && (
        <div>
          <p className="text-[11px] uppercase tracking-wider text-zinc-500 font-medium mb-2 px-1">Completed</p>
          <div className="space-y-0.5">
            {done.map((t) => (
              <button
                key={t.id}
                onClick={() => handleToggle(t)}
                className="w-full flex items-start gap-3 px-3 py-3 rounded-xl hover:bg-white/[0.03] transition-colors text-left opacity-50"
              >
                <CheckCircle2 className="w-[18px] h-[18px] text-emerald-500 shrink-0 mt-0.5" />
                <p className="text-[15px] text-zinc-500 line-through">{t.title}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {ws.tasks.length === 0 && (
        <p className="text-[15px] text-zinc-600 italic">No tasks yet. Add one above.</p>
      )}
    </div>
  )
}

/* ─── Notifications View ─────────────────────────────────────── */

function NotificationsView({ notifs }: { notifs: NotificationOut[] }) {
  const unread = notifs.filter((n) => !n.is_read)
  const read = notifs.filter((n) => n.is_read)

  return (
    <div className="flex-1 overflow-y-auto p-8 max-w-2xl">
      <h2 className="text-[18px] font-semibold text-foreground mb-6">
        Notifications {unread.length > 0 && <span className="text-zinc-500 font-normal text-[15px]">· {unread.length} unread</span>}
      </h2>

      {notifs.length === 0 ? (
        <p className="text-[15px] text-zinc-600 italic">No notifications for this case.</p>
      ) : (
        <div className="space-y-1">
          {[...unread, ...read].map((item) => (
            <div
              key={item.id}
              className={cn(
                'flex items-start gap-3 px-3 py-3 rounded-xl transition-colors',
                !item.is_read ? 'bg-white/[0.03]' : 'hover:bg-white/[0.02]'
              )}
            >
              {!item.is_read && <div className="w-2 h-2 rounded-full bg-blue-400 shrink-0 mt-2" />}
              <div className={cn('flex-1 min-w-0', item.is_read && 'ml-5')}>
                <div className="flex items-center gap-2">
                  <p className="text-[15px] text-zinc-200 font-medium leading-snug">{item.title}</p>
                  <span className={cn(
                    'text-[10px] px-1.5 py-0.5 rounded-full font-medium border',
                    item.priority === 'high' ? 'bg-red-400/10 text-red-400 border-red-400/20' :
                    item.priority === 'medium' ? 'bg-amber-400/10 text-amber-400 border-amber-400/20' :
                    'bg-zinc-400/10 text-zinc-400 border-zinc-400/20'
                  )}>
                    {item.priority}
                  </span>
                </div>
                {item.description && <p className="text-[13px] text-zinc-500 mt-1 leading-relaxed">{item.description}</p>}
                <div className="flex items-center gap-2 mt-1.5">
                  {item.agent_name && <span className="text-[11px] text-zinc-600">{item.agent_name}</span>}
                  <span className="text-[11px] text-zinc-700">{new Date(item.created_at).toLocaleString()}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/* ─── Chat Bubble ────────────────────────────────────────────── */

function ChatBubble({ msg }: { msg: WorkspaceMessageOut }) {
  const isUser = msg.role === 'user'
  const isActivity = msg.role === 'activity'
  const AgentIcon = resolveIcon(msg.agent_icon)

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] bg-white/[0.07] rounded-[20px] rounded-br-sm px-5 py-3.5">
          <p className="text-[15px] text-foreground leading-[1.7] whitespace-pre-line">{msg.content}</p>
        </div>
      </div>
    )
  }

  if (isActivity) {
    return (
      <div className="flex items-center gap-3 py-2">
        <div className="h-px flex-1 bg-white/[0.04]" />
        <span className="text-[12px] text-zinc-600 font-medium">{msg.content}</span>
        <div className="h-px flex-1 bg-white/[0.04]" />
      </div>
    )
  }

  return (
    <div className="flex items-start gap-3">
      <div
        className="w-9 h-9 rounded-full flex items-center justify-center shrink-0 mt-1"
        style={{ backgroundColor: msg.agent_color ? `${msg.agent_color}20` : 'rgba(255,255,255,0.08)' }}
      >
        <AgentIcon className="w-4 h-4" style={{ color: msg.agent_color || '#999' }} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-[14px] font-semibold text-zinc-100">{msg.agent_name}</span>
        </div>
        <div className="bg-white/[0.03] rounded-[20px] rounded-tl-sm px-5 py-3.5">
          <p className="text-[15px] text-zinc-300 leading-[1.7] whitespace-pre-line">{msg.content}</p>
        </div>
      </div>
    </div>
  )
}
