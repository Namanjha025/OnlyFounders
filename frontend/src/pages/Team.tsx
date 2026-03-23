import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Users, Loader2, X, Pencil, Trash2, Plus, Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import { team as teamApi, agents as agentsApi, type TeamAgentOut, type AgentOut } from '@/lib/api'
import { resolveIcon } from '@/lib/icons'
import { avatarGradient, scoreToColor, EntityCard, CardSkeleton } from '@/components/shared'

export function Team() {
  const [members, setMembers] = useState<TeamAgentOut[]>([])
  const [catalogAgents, setCatalogAgents] = useState<AgentOut[]>([])
  const [loading, setLoading] = useState(true)
  const [showHire, setShowHire] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editRole, setEditRole] = useState('')
  const [editJd, setEditJd] = useState('')

  useEffect(() => {
    Promise.all([teamApi.list(), agentsApi.list()])
      .then(([t, a]) => { setMembers(t); setCatalogAgents(a) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const hiredIds = new Set(members.map((m) => m.agent_id))
  const available = catalogAgents.filter((a) => !hiredIds.has(a.id))

  const handleHire = async (agent: AgentOut) => {
    try {
      const ta = await teamApi.hire({ agent_id: agent.id, role: agent.name, job_description: agent.description || undefined })
      setMembers((prev) => [...prev, ta])
    } catch {}
  }

  const handleRemove = async (id: string) => {
    try {
      await teamApi.remove(id)
      setMembers((prev) => prev.filter((m) => m.id !== id))
    } catch {}
  }

  const startEdit = (m: TeamAgentOut) => {
    setEditingId(m.id)
    setEditRole(m.role || '')
    setEditJd(m.job_description || '')
  }

  const saveEdit = async () => {
    if (!editingId) return
    try {
      const updated = await teamApi.update(editingId, { role: editRole, job_description: editJd })
      setMembers((prev) => prev.map((m) => (m.id === editingId ? updated : m)))
    } catch {}
    setEditingId(null)
  }

  const agentById = (id: string) => catalogAgents.find((a) => a.id === id)

  if (loading) {
    return (
      <div className="animate-fade-in -m-8 min-h-screen bg-[#050507]">
        <div className="mx-auto max-w-[1400px] px-6 py-8 sm:px-8">
          <div className="h-8 w-32 bg-secondary rounded animate-pulse mb-6" />
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />)}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="animate-fade-in -m-8 min-h-screen bg-[#050507]">
      <div className="mx-auto max-w-[1400px] px-6 py-8 pb-16 sm:px-8">
        {/* Header */}
        <header className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Users className="w-5 h-5 text-muted-foreground" />
                <h1 className="text-2xl font-semibold text-foreground tracking-tight">My Team</h1>
              </div>
              <p className="mt-1 max-w-xl text-[15px] text-muted-foreground">
                Your startup's hired agents. Assign them to cases to get work done.
              </p>
            </div>
            <button
              onClick={() => setShowHire(!showHire)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-xl text-[14px] font-medium transition-colors',
                showHire
                  ? 'bg-white/[0.08] text-white'
                  : 'bg-white text-black hover:bg-zinc-200'
              )}
            >
              {showHire ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
              {showHire ? 'Close' : 'Hire Agent'}
            </button>
          </div>
        </header>

        {/* Hire panel — uses EntityCard grid */}
        {showHire && (
          <div className="mb-8">
            <p className="text-[13px] uppercase tracking-wider text-zinc-500 font-medium mb-4">Available Agents</p>
            {available.length === 0 ? (
              <p className="text-[14px] text-zinc-500">All agents are already on your team.</p>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {available.map((agent) => {
                  const Icon = resolveIcon(agent.icon)
                  const capCount = agent.capabilities?.length ?? 0
                  const capScore = Math.min(capCount / 10, 1)
                  return (
                    <div key={agent.id} className="relative group">
                      <EntityCard
                        to={`/agents/${agent.id}`}
                        avatarContent={
                          <div className="w-full h-full flex items-center justify-center"
                            style={{ background: avatarGradient(agent.name) }}>
                            <Icon className="w-7 h-7" style={{ color: agent.color || '#ccc' }} />
                          </div>
                        }
                        ringProgress={capScore}
                        ringColor={scoreToColor(capScore * 100)}
                        name={agent.name}
                        type={agent.category || 'General'}
                        description={agent.description}
                        tags={agent.capabilities ?? undefined}
                      />
                      <button
                        onClick={(e) => { e.preventDefault(); handleHire(agent) }}
                        className="absolute top-3 right-3 px-3 py-1.5 rounded-lg text-[12px] font-medium bg-white text-black hover:bg-zinc-200 transition-colors opacity-0 group-hover:opacity-100 z-10"
                      >
                        Hire
                      </button>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}

        {/* Team members — uses EntityCard grid */}
        {members.length === 0 ? (
          <div className="text-center py-20">
            <Users className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
            <p className="text-[16px] text-zinc-400 font-medium">No agents on your team yet</p>
            <p className="text-[14px] text-zinc-600 mt-1">Hire agents from the catalog to build your team.</p>
          </div>
        ) : (
          <>
            <p className="text-[13px] uppercase tracking-wider text-zinc-500 font-medium mb-4">
              Team Members ({members.length})
            </p>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {members.map((m) => {
                const agent = agentById(m.agent_id)
                const Icon = resolveIcon(m.agent_icon)
                const capCount = m.agent_capabilities?.length ?? 0
                const capScore = Math.min(capCount / 10, 1)
                const isEditing = editingId === m.id

                if (isEditing) {
                  return (
                    <div key={m.id} className="rounded-2xl border border-border bg-card p-6">
                      <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 rounded-full flex items-center justify-center"
                          style={{ background: avatarGradient(m.agent_name) }}>
                          <Icon className="w-5 h-5" style={{ color: m.agent_color || '#ccc' }} />
                        </div>
                        <div>
                          <p className="text-[15px] font-semibold text-foreground">{m.agent_name}</p>
                          <p className="text-[12px] text-muted-foreground capitalize">{m.agent_category}</p>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <input
                          className="w-full px-3 py-2 rounded-lg bg-white/[0.06] border border-white/[0.1] text-[13px] text-foreground outline-none focus:border-white/[0.2]"
                          placeholder="Role (e.g. Head of Content)"
                          value={editRole}
                          onChange={(e) => setEditRole(e.target.value)}
                        />
                        <textarea
                          className="w-full px-3 py-2 rounded-lg bg-white/[0.06] border border-white/[0.1] text-[13px] text-foreground outline-none focus:border-white/[0.2] resize-none"
                          placeholder="Job description..."
                          rows={3}
                          value={editJd}
                          onChange={(e) => setEditJd(e.target.value)}
                        />
                        <div className="flex gap-2">
                          <button onClick={saveEdit} className="px-3 py-1.5 rounded-lg text-[12px] font-medium bg-white text-black hover:bg-zinc-200 transition-colors">
                            Save
                          </button>
                          <button onClick={() => setEditingId(null)} className="px-3 py-1.5 rounded-lg text-[12px] font-medium bg-white/[0.06] text-zinc-400 hover:text-white transition-colors">
                            Cancel
                          </button>
                        </div>
                      </div>
                    </div>
                  )
                }

                return (
                  <div key={m.id} className="relative group">
                    <EntityCard
                      to={`/agents/${m.agent_id}`}
                      avatarContent={
                        <div className="w-full h-full flex items-center justify-center"
                          style={{ background: avatarGradient(m.agent_name) }}>
                          <Icon className="w-7 h-7" style={{ color: m.agent_color || '#ccc' }} />
                        </div>
                      }
                      ringProgress={capScore}
                      ringColor={scoreToColor(capScore * 100)}
                      name={m.agent_name}
                      subtitle={m.role || null}
                      type={m.agent_category || 'General'}
                      description={m.job_description}
                      tags={m.agent_capabilities ?? undefined}
                      badge={true}
                    />
                    <div className="absolute top-3 right-3 flex items-center gap-1 opacity-0 group-hover:opacity-100 z-10 transition-opacity">
                      <button
                        onClick={(e) => { e.preventDefault(); startEdit(m) }}
                        className="p-1.5 rounded-lg bg-card/90 border border-white/[0.08] text-zinc-400 hover:text-white hover:bg-white/[0.1] transition-colors"
                        title="Edit role"
                      >
                        <Pencil className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={(e) => { e.preventDefault(); handleRemove(m.id) }}
                        className="p-1.5 rounded-lg bg-card/90 border border-white/[0.08] text-zinc-400 hover:text-red-400 hover:bg-white/[0.1] transition-colors"
                        title="Remove from team"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                )
              })}
            </div>
          </>
        )}
      </div>
    </div>
  )
}
