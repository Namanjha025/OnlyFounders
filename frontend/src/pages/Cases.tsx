import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
  Plus, Loader2, CheckCircle2, Clock, Circle, ChevronRight, X, Search,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { resolveIcon } from '@/lib/icons'
import {
  workspaces as wsApi,
  team as teamApi,
  agents as agentsApi,
  type WorkspaceSummary,
  type CaseStatus,
  type TeamAgentOut,
  type AgentOut,
} from '@/lib/api'

const STATUS_CONFIG: Record<CaseStatus, { label: string; color: string; bg: string; border: string; icon: typeof Circle }> = {
  open: { label: 'Open', color: 'text-blue-400', bg: 'bg-blue-400/10', border: 'border-blue-400/20', icon: Circle },
  in_progress: { label: 'In Progress', color: 'text-amber-400', bg: 'bg-amber-400/10', border: 'border-amber-400/20', icon: Clock },
  resolved: { label: 'Resolved', color: 'text-emerald-400', bg: 'bg-emerald-400/10', border: 'border-emerald-400/20', icon: CheckCircle2 },
}

const ICON_OPTIONS = ['Megaphone', 'Scale', 'TrendingUp', 'Bot', 'Code', 'Briefcase', 'Search', 'PenTool', 'BarChart3', 'Users', 'Shield', 'Palette']

export function Cases() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [cases, setCases] = useState<WorkspaceSummary[]>([])
  const [teamList, setTeamList] = useState<TeamAgentOut[]>([])
  const [catalog, setCatalog] = useState<AgentOut[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<CaseStatus | 'all'>('all')
  const [showCreate, setShowCreate] = useState(searchParams.get('new') === '1')

  useEffect(() => {
    Promise.all([wsApi.list(), teamApi.list(), agentsApi.list()])
      .then(([c, t, a]) => { setCases(c); setTeamList(t); setCatalog(a) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const filtered = filter === 'all' ? cases : cases.filter((c) => c.case_status === filter)

  const counts = {
    all: cases.length,
    open: cases.filter((c) => c.case_status === 'open').length,
    in_progress: cases.filter((c) => c.case_status === 'in_progress').length,
    resolved: cases.filter((c) => c.case_status === 'resolved').length,
  }

  const handleCreated = (ws: WorkspaceSummary) => {
    setCases((prev) => [ws, ...prev])
    setShowCreate(false)
    navigate(`/cases/${ws.id}`)
  }

  if (loading) {
    return (
      <div className="animate-fade-in -m-8 h-screen flex items-center justify-center bg-[#050507]">
        <Loader2 className="w-5 h-5 text-zinc-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="animate-fade-in -m-8 min-h-screen flex flex-col bg-[#050507]">
      <div className="flex-1 flex flex-col px-6 pt-10 pb-10">
        <div className="max-w-4xl mx-auto w-full">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-semibold text-foreground tracking-tight">Cases</h1>
              <p className="text-[15px] text-muted-foreground mt-1">
                Open a case for a task or project. Assign agents and track progress.
              </p>
            </div>
            <button
              onClick={() => setShowCreate(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-[14px] font-medium bg-white text-black hover:bg-zinc-200 transition-colors"
            >
              <Plus className="w-4 h-4" />
              New Case
            </button>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-2 mb-6">
            {(['all', 'open', 'in_progress', 'resolved'] as const).map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={cn(
                  'px-3 py-1.5 rounded-lg text-[13px] font-medium transition-colors',
                  filter === f
                    ? 'bg-white/[0.1] text-white'
                    : 'text-zinc-500 hover:text-zinc-300 hover:bg-white/[0.04]'
                )}
              >
                {f === 'all' ? 'All' : STATUS_CONFIG[f].label}
                <span className="ml-1.5 text-[11px] text-zinc-600">{counts[f]}</span>
              </button>
            ))}
          </div>

          {/* Case list */}
          {filtered.length === 0 ? (
            <div className="text-center py-16">
              <Circle className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
              <p className="text-[16px] text-zinc-400 font-medium">
                {filter === 'all' ? 'No cases yet' : `No ${STATUS_CONFIG[filter as CaseStatus].label.toLowerCase()} cases`}
              </p>
              <p className="text-[14px] text-zinc-600 mt-1">Create a case to get started.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {filtered.map((c) => {
                const Icon = resolveIcon(c.icon)
                const status = STATUS_CONFIG[c.case_status] || STATUS_CONFIG.open
                const StatusIcon = status.icon

                return (
                  <button
                    key={c.id}
                    onClick={() => navigate(`/cases/${c.id}`)}
                    className="w-full text-left rounded-xl border border-white/[0.06] bg-white/[0.02] p-5 transition-all hover:bg-white/[0.05] hover:border-white/[0.12] group"
                  >
                    <div className="flex items-start gap-4">
                      <div className="w-11 h-11 rounded-xl flex items-center justify-center shrink-0 bg-white/[0.04]">
                        <Icon className="w-5 h-5 text-zinc-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2.5 mb-1">
                          <h3 className="text-[15px] font-medium text-foreground">{c.name}</h3>
                          <span className={cn('text-[11px] px-2 py-0.5 rounded-full font-medium border flex items-center gap-1', status.bg, status.color, status.border)}>
                            <StatusIcon className="w-3 h-3" />
                            {status.label}
                          </span>
                        </div>
                        {c.status_text && (
                          <p className="text-[13px] text-zinc-500 mb-2">{c.status_text}</p>
                        )}
                        <div className="flex items-center gap-4 text-[12px] text-zinc-600">
                          <span>{c.agent_count} agent{c.agent_count !== 1 ? 's' : ''}</span>
                          <span>{c.task_done_count}/{c.task_total_count} tasks done</span>
                          {c.notification_count > 0 && (
                            <span className="text-red-400">{c.notification_count} notification{c.notification_count !== 1 ? 's' : ''}</span>
                          )}
                        </div>
                        {c.progress != null && (
                          <div className="flex items-center gap-2 mt-3">
                            <div className="flex-1 h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                              <div className="h-full bg-white/50 rounded-full transition-all" style={{ width: `${c.progress}%` }} />
                            </div>
                            <span className="text-[11px] text-zinc-500 font-medium">{c.progress}%</span>
                          </div>
                        )}
                      </div>
                      <ChevronRight className="w-5 h-5 text-zinc-700 shrink-0 mt-1 group-hover:text-zinc-400 transition-colors" />
                    </div>
                  </button>
                )
              })}
            </div>
          )}
        </div>
      </div>

      {showCreate && (
        <NewCaseModal
          catalog={catalog}
          teamAgents={teamList}
          onClose={() => setShowCreate(false)}
          onCreated={handleCreated}
          onTeamUpdated={setTeamList}
        />
      )}
    </div>
  )
}

function NewCaseModal({
  catalog,
  teamAgents,
  onClose,
  onCreated,
  onTeamUpdated,
}: {
  catalog: AgentOut[]
  teamAgents: TeamAgentOut[]
  onClose: () => void
  onCreated: (ws: WorkspaceSummary) => void
  onTeamUpdated: (team: TeamAgentOut[]) => void
}) {
  const [name, setName] = useState('')
  const [goal, setGoal] = useState('')
  const [icon, setIcon] = useState('Briefcase')
  const [selectedAgents, setSelectedAgents] = useState<Set<string>>(new Set())
  const [creating, setCreating] = useState(false)
  const [search, setSearch] = useState('')

  const hiredIds = new Set(teamAgents.map((ta) => ta.agent_id))
  const query = search.toLowerCase().trim()
  const filtered = query
    ? catalog.filter((a) => a.name.toLowerCase().includes(query) || (a.category || '').toLowerCase().includes(query))
    : catalog
  const yourAgents = filtered.filter((a) => hiredIds.has(a.id))
  const otherAgents = filtered.filter((a) => !hiredIds.has(a.id))

  const toggleAgent = (agentId: string) => {
    setSelectedAgents((prev) => {
      const next = new Set(prev)
      if (next.has(agentId)) next.delete(agentId)
      else next.add(agentId)
      return next
    })
  }

  const handleCreate = async () => {
    if (!name.trim()) return
    setCreating(true)
    try {
      const ws = await wsApi.create({
        name: name.trim(),
        workspace_type: 'goal',
        case_status: 'open',
        goal: goal.trim() || undefined,
        icon,
      })

      const newTeamMembers: TeamAgentOut[] = []
      for (const agentId of selectedAgents) {
        await wsApi.addAgent(ws.id, agentId)
        if (!hiredIds.has(agentId)) {
          try {
            const hired = await teamApi.hire({ agent_id: agentId })
            newTeamMembers.push(hired)
          } catch { /* already hired or error — skip */ }
        }
      }

      if (newTeamMembers.length > 0) {
        onTeamUpdated([...teamAgents, ...newTeamMembers])
      }

      const summary: WorkspaceSummary = {
        id: ws.id,
        name: ws.name,
        workspace_type: ws.workspace_type,
        case_status: ws.case_status,
        icon: ws.icon,
        status_text: ws.status_text,
        progress: ws.progress,
        agent_count: selectedAgents.size,
        task_done_count: 0,
        task_total_count: 0,
        notification_count: 0,
        created_at: ws.created_at,
      }
      onCreated(summary)
    } catch {}
    setCreating(false)
  }

  const renderAgentButton = (agent: AgentOut) => {
    const AgentIcon = resolveIcon(agent.icon)
    const selected = selectedAgents.has(agent.id)
    return (
      <button
        key={agent.id}
        onClick={() => toggleAgent(agent.id)}
        className={cn(
          'flex items-center gap-2.5 px-3 py-2.5 rounded-lg border transition-colors text-left',
          selected
            ? 'bg-white/[0.08] border-white/[0.15] text-white'
            : 'bg-white/[0.02] border-white/[0.06] text-zinc-400 hover:bg-white/[0.04]'
        )}
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
        {selected && <CheckCircle2 className="w-4 h-4 text-white shrink-0" />}
      </button>
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative w-full max-w-xl max-h-[85vh] overflow-y-auto rounded-2xl border border-white/[0.08] bg-[#0c0c10] shadow-2xl mx-4">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 text-zinc-500 hover:text-white hover:bg-white/[0.06] rounded-lg transition-colors z-10"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="p-8">
          <h2 className="text-xl font-semibold text-foreground mb-6">New Case</h2>

          {/* Name */}
          <div className="mb-5">
            <label className="text-[12px] uppercase tracking-wider text-zinc-500 font-medium mb-2 block">Case Name</label>
            <input
              className="w-full px-4 py-2.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-[14px] text-foreground placeholder-zinc-600 outline-none focus:border-white/[0.16] transition-colors"
              placeholder="e.g. Product Launch, Legal Setup, Hiring Sprint..."
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
          </div>

          {/* Goal */}
          <div className="mb-5">
            <label className="text-[12px] uppercase tracking-wider text-zinc-500 font-medium mb-2 block">Goal (optional)</label>
            <textarea
              className="w-full px-4 py-2.5 rounded-xl bg-white/[0.04] border border-white/[0.08] text-[14px] text-foreground placeholder-zinc-600 outline-none focus:border-white/[0.16] transition-colors resize-none"
              placeholder="What do you want to achieve with this case?"
              rows={2}
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
            />
          </div>

          {/* Icon */}
          <div className="mb-6">
            <label className="text-[12px] uppercase tracking-wider text-zinc-500 font-medium mb-2 block">Icon</label>
            <div className="flex flex-wrap gap-2">
              {ICON_OPTIONS.map((ico) => {
                const Ico = resolveIcon(ico)
                return (
                  <button
                    key={ico}
                    onClick={() => setIcon(ico)}
                    className={cn(
                      'w-9 h-9 rounded-lg flex items-center justify-center transition-colors border',
                      icon === ico
                        ? 'bg-white/[0.1] border-white/[0.2] text-white'
                        : 'bg-white/[0.03] border-white/[0.06] text-zinc-500 hover:text-zinc-300 hover:bg-white/[0.06]'
                    )}
                  >
                    <Ico className="w-4 h-4" />
                  </button>
                )
              })}
            </div>
          </div>

          {/* Assign agents from catalog */}
          {catalog.length > 0 && (
            <div className="mb-6">
              <label className="text-[12px] uppercase tracking-wider text-zinc-500 font-medium mb-2 block">
                Assign Agents ({selectedAgents.size} selected)
              </label>

              <div className="relative mb-3">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-600" />
                <input
                  className="w-full pl-8 pr-3 py-2 rounded-lg bg-white/[0.04] border border-white/[0.08] text-[13px] text-foreground placeholder-zinc-600 outline-none focus:border-white/[0.16] transition-colors"
                  placeholder="Search agents..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
              </div>

              <div className="max-h-56 overflow-y-auto space-y-3">
                {yourAgents.length > 0 && (
                  <div>
                    <p className="text-[11px] uppercase tracking-wider text-zinc-600 font-medium mb-1.5 px-0.5">Your agents</p>
                    <div className="grid grid-cols-2 gap-2">
                      {yourAgents.map(renderAgentButton)}
                    </div>
                  </div>
                )}
                {otherAgents.length > 0 && (
                  <div>
                    <p className="text-[11px] uppercase tracking-wider text-zinc-600 font-medium mb-1.5 px-0.5">All agents</p>
                    <div className="grid grid-cols-2 gap-2">
                      {otherAgents.map(renderAgentButton)}
                    </div>
                  </div>
                )}
                {filtered.length === 0 && (
                  <p className="text-[13px] text-zinc-600 text-center py-4">No agents match your search.</p>
                )}
              </div>
            </div>
          )}

          {/* Submit */}
          <button
            onClick={handleCreate}
            disabled={!name.trim() || creating}
            className={cn(
              'w-full py-3 rounded-xl text-[15px] font-semibold transition-colors',
              name.trim() && !creating
                ? 'bg-white text-black hover:bg-zinc-200'
                : 'bg-white/[0.06] text-zinc-600 cursor-not-allowed'
            )}
          >
            {creating ? 'Creating...' : 'Create Case'}
          </button>
        </div>
      </div>
    </div>
  )
}
