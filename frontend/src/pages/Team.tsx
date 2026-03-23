import { useState, useEffect } from 'react'
import { Users, Loader2, X, Pencil, Trash2, Plus } from 'lucide-react'
import { cn } from '@/lib/utils'
import { team as teamApi, agents as agentsApi, type TeamAgentOut, type AgentOut } from '@/lib/api'
import { resolveIcon } from '@/lib/icons'
import { AgentProfileModal } from '@/components/AgentProfileModal'

export function Team() {
  const [members, setMembers] = useState<TeamAgentOut[]>([])
  const [catalogAgents, setCatalogAgents] = useState<AgentOut[]>([])
  const [loading, setLoading] = useState(true)
  const [showHire, setShowHire] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editRole, setEditRole] = useState('')
  const [editJd, setEditJd] = useState('')
  const [profileAgent, setProfileAgent] = useState<AgentOut | null>(null)

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
          <div className="flex items-center justify-between mb-2">
            <div>
              <h1 className="text-2xl font-semibold text-foreground tracking-tight">My Team</h1>
              <p className="text-[15px] text-muted-foreground mt-1">
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

          {/* Hire panel */}
          {showHire && (
            <div className="mt-6 p-5 rounded-2xl border border-white/[0.08] bg-white/[0.02]">
              <h2 className="text-[13px] uppercase tracking-wider text-zinc-500 font-medium mb-4">Available Agents</h2>
              {available.length === 0 ? (
                <p className="text-[14px] text-zinc-500">All agents are already on your team.</p>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {available.map((agent) => {
                    const Icon = resolveIcon(agent.icon)
                    return (
                      <div
                        key={agent.id}
                        className="flex items-center gap-3 px-4 py-3 rounded-xl bg-white/[0.03] border border-white/[0.06] group"
                      >
                        <div
                          className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
                          style={{ backgroundColor: agent.color ? `${agent.color}15` : 'rgba(255,255,255,0.06)' }}
                        >
                          <Icon className="w-4 h-4" style={{ color: agent.color || '#999' }} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-[14px] font-medium text-foreground truncate">{agent.name}</p>
                          <p className="text-[12px] text-zinc-500 truncate">{agent.category}</p>
                        </div>
                        <button
                          onClick={() => handleHire(agent)}
                          className="px-3 py-1.5 rounded-lg text-[12px] font-medium bg-white/[0.08] text-zinc-300 hover:bg-white/[0.15] hover:text-white transition-colors"
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

          {/* Team members */}
          {members.length === 0 ? (
            <div className="mt-16 text-center">
              <Users className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
              <p className="text-[16px] text-zinc-400 font-medium">No agents on your team yet</p>
              <p className="text-[14px] text-zinc-600 mt-1">Hire agents from the catalog to build your team.</p>
            </div>
          ) : (
            <div className="mt-8 space-y-3">
              {members.map((m) => {
                const Icon = resolveIcon(m.agent_icon)
                const isEditing = editingId === m.id

                return (
                  <div
                    key={m.id}
                    className="rounded-xl border border-white/[0.06] bg-white/[0.02] p-4 transition-all hover:bg-white/[0.04]"
                  >
                    <div className="flex items-start gap-4">
                      <button
                        onClick={() => {
                          const agent = catalogAgents.find((a) => a.id === m.agent_id)
                          if (agent) setProfileAgent(agent)
                        }}
                        className="shrink-0"
                      >
                        <div
                          className="w-11 h-11 rounded-xl flex items-center justify-center transition-transform hover:scale-105"
                          style={{ backgroundColor: m.agent_color ? `${m.agent_color}15` : 'rgba(255,255,255,0.06)' }}
                        >
                          <Icon className="w-5 h-5" style={{ color: m.agent_color || '#999' }} />
                        </div>
                      </button>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="text-[15px] font-medium text-foreground">{m.agent_name}</p>
                          <span
                            className="text-[11px] px-2 py-0.5 rounded-full font-medium"
                            style={{
                              backgroundColor: m.agent_color ? `${m.agent_color}10` : 'rgba(255,255,255,0.05)',
                              color: m.agent_color || '#999',
                            }}
                          >
                            {m.agent_category}
                          </span>
                        </div>

                        {isEditing ? (
                          <div className="mt-3 space-y-2">
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
                        ) : (
                          <>
                            <p className="text-[13px] text-zinc-400 mt-0.5">{m.role}</p>
                            {m.job_description && (
                              <p className="text-[13px] text-zinc-500 mt-1 leading-relaxed line-clamp-2">{m.job_description}</p>
                            )}
                            {m.agent_capabilities && m.agent_capabilities.length > 0 && (
                              <div className="flex flex-wrap gap-1.5 mt-2.5">
                                {m.agent_capabilities.map((cap) => (
                                  <span key={cap} className="text-[11px] px-2 py-0.5 rounded-full bg-white/[0.05] text-zinc-400 font-medium">{cap}</span>
                                ))}
                              </div>
                            )}
                          </>
                        )}
                      </div>
                      {!isEditing && (
                        <div className="flex items-center gap-1 shrink-0">
                          <button
                            onClick={() => startEdit(m)}
                            className="p-2 text-zinc-600 hover:text-zinc-300 hover:bg-white/[0.06] rounded-lg transition-colors"
                            title="Edit role"
                          >
                            <Pencil className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleRemove(m.id)}
                            className="p-2 text-zinc-600 hover:text-red-400 hover:bg-white/[0.06] rounded-lg transition-colors"
                            title="Remove from team"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>

      {profileAgent && (
        <AgentProfileModal
          agent={{
            id: profileAgent.id,
            name: profileAgent.name,
            icon: resolveIcon(profileAgent.icon),
            color: profileAgent.color || '#999',
            category: profileAgent.category || 'General',
            description: profileAgent.description || '',
            capabilities: profileAgent.capabilities ?? [],
            instructions: profileAgent.instructions ?? [],
            connections: profileAgent.connections ?? [],
          }}
          open={true}
          onClose={() => setProfileAgent(null)}
        />
      )}
    </div>
  )
}
