import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Bot, CheckCircle2, Plug, Sparkles, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { agents as agentsApi, team as teamApi, type AgentOut, type TeamAgentOut } from '@/lib/api'
import { resolveIcon } from '@/lib/icons'

export function AgentProfile() {
  const { agentId } = useParams<{ agentId: string }>()
  const [agent, setAgent] = useState<AgentOut | null>(null)
  const [teamList, setTeamList] = useState<TeamAgentOut[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!agentId) return
    Promise.all([agentsApi.get(agentId), teamApi.list()])
      .then(([a, t]) => { setAgent(a); setTeamList(t) })
      .catch((err) => setError(err instanceof Error ? err.message : 'Not found'))
      .finally(() => setLoading(false))
  }, [agentId])

  const isHired = agent ? teamList.some((t) => t.agent_id === agent.id) : false

  const handleHire = async () => {
    if (!agent || isHired) return
    try {
      const ta = await teamApi.hire({ agent_id: agent.id })
      setTeamList((prev) => [...prev, ta])
    } catch {}
  }

  if (loading) return (
    <div className="animate-fade-in -m-8 min-h-screen bg-background flex items-center justify-center">
      <Loader2 className="w-5 h-5 text-zinc-500 animate-spin" />
    </div>
  )
  if (error) return (
    <div className="animate-fade-in -m-8 min-h-screen bg-background px-6 py-10">
      <div className="max-w-xl mx-auto text-center py-20">
        <p className="text-red-400 mb-4">{error}</p>
        <Link to="/agents" className="text-zinc-300 hover:underline text-sm">Back to agents</Link>
      </div>
    </div>
  )
  if (!agent) return null

  const Icon = resolveIcon(agent.icon)
  const capabilities = agent.capabilities ?? []
  const instructions = agent.instructions ?? []
  const connections = agent.connections ?? []

  return (
    <div className="animate-fade-in -m-8 min-h-screen bg-background text-white">
      {/* Top bar */}
      <div className="border-b border-border bg-background/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-3 flex items-center justify-between">
          <Link to="/agents" className="flex items-center gap-2 text-sm text-zinc-400 hover:text-zinc-300 transition">
            <ArrowLeft className="w-4 h-4" /> Back to agents
          </Link>
          <button
            onClick={handleHire}
            disabled={isHired}
            className={cn(
              'flex items-center gap-2 px-4 py-1.5 rounded-lg text-sm font-semibold transition',
              isHired
                ? 'bg-white/[0.06] text-zinc-500 cursor-default'
                : 'bg-white text-black hover:bg-zinc-300'
            )}
          >
            {isHired ? 'On Your Team' : 'Hire to Team'}
          </button>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-6">

          {/* Left column */}
          <div className="space-y-6">
            {/* Hero card */}
            <div className="rounded-2xl border border-border bg-card p-8">
              <div className="flex flex-col items-center">
                <div
                  className="w-20 h-20 rounded-2xl flex items-center justify-center mb-4"
                  style={{ backgroundColor: agent.color ? `${agent.color}15` : 'rgba(255,255,255,0.06)' }}
                >
                  <Icon className="w-10 h-10" style={{ color: agent.color || '#999' }} />
                </div>
                <h1 className="text-2xl font-semibold">{agent.name}</h1>
                <p className="text-sm text-zinc-400 capitalize mt-1">{agent.category || 'General'}</p>
                <div className="flex items-center gap-2 mt-3">
                  <span
                    className="text-[12px] px-2.5 py-1 rounded-full font-medium border"
                    style={{ backgroundColor: `${agent.color || '#999'}10`, color: agent.color || '#999', borderColor: `${agent.color || '#999'}30` }}
                  >
                    {agent.category || 'General'}
                  </span>
                  <span className="text-[12px] px-2.5 py-1 rounded-full bg-white/[0.05] text-zinc-400 font-medium border border-white/[0.08]">
                    Platform Agent
                  </span>
                </div>
              </div>
            </div>

            {/* About */}
            {agent.description && (
              <div className="rounded-2xl border border-border bg-card p-6">
                <h2 className="font-semibold text-[15px] text-foreground mb-3">About</h2>
                <div className="border-l-2 border-white/30 pl-4">
                  <p className="text-sm text-zinc-300 leading-relaxed">{agent.description}</p>
                </div>
              </div>
            )}

            {/* Capabilities */}
            {capabilities.length > 0 && (
              <div className="rounded-2xl border border-border bg-card p-6">
                <h2 className="flex items-center gap-2 font-semibold text-[15px] text-foreground mb-4">
                  <Bot className="w-4 h-4 text-zinc-400" />
                  Capabilities
                </h2>
                <div className="flex flex-wrap gap-2">
                  {capabilities.map((cap) => (
                    <span
                      key={cap}
                      className="text-[13px] px-3 py-1.5 rounded-lg bg-white/[0.04] text-zinc-300 font-medium border border-white/[0.06]"
                    >
                      {cap}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Instructions */}
            {instructions.length > 0 && (
              <div className="rounded-2xl border border-border bg-card p-6">
                <h2 className="flex items-center gap-2 font-semibold text-[15px] text-foreground mb-4">
                  <CheckCircle2 className="w-4 h-4 text-zinc-400" />
                  Agent Instructions
                </h2>
                <div className="space-y-3">
                  {instructions.map((instruction, i) => (
                    <div key={i} className="flex items-start gap-2.5">
                      <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                      <p className="text-[14px] text-zinc-300 leading-relaxed">{instruction}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Connections */}
            {connections.length > 0 && (
              <div className="rounded-2xl border border-border bg-card p-6">
                <h2 className="flex items-center gap-2 font-semibold text-[15px] text-foreground mb-4">
                  <Plug className="w-4 h-4 text-zinc-400" />
                  Connections & Integrations
                </h2>
                <div className="grid grid-cols-2 gap-3">
                  {connections.map((conn) => (
                    <div
                      key={conn.name}
                      className="flex items-center gap-2.5 px-4 py-3 rounded-xl bg-white/[0.03] border border-white/[0.06]"
                    >
                      <div className="w-8 h-8 rounded-lg bg-white/[0.08] flex items-center justify-center text-[11px] font-bold text-zinc-400">
                        {conn.name.charAt(0)}
                      </div>
                      <span className="text-[13px] text-zinc-300 font-medium">{conn.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right column */}
          <div className="space-y-4">
            {/* Hire card */}
            <div className="rounded-2xl border border-border bg-card p-5">
              <h3 className="font-semibold text-[15px] text-foreground mb-3">Add to Team</h3>
              <p className="text-xs text-zinc-500 mb-4">
                {isHired
                  ? 'This agent is on your team. Assign it to cases anytime.'
                  : 'Hire this agent to your team — then assign it to any case.'}
              </p>
              <button
                onClick={handleHire}
                disabled={isHired}
                className={cn(
                  'w-full py-2.5 rounded-xl text-sm font-semibold transition',
                  isHired
                    ? 'bg-white/[0.06] text-zinc-500 cursor-default'
                    : 'bg-white text-black hover:bg-zinc-200'
                )}
              >
                {isHired ? 'Already on Team' : 'Hire to Team'}
              </button>
            </div>

            {/* Quick info */}
            <div className="rounded-2xl border border-border bg-card p-5">
              <h3 className="font-semibold text-[15px] text-foreground mb-3">Quick Info</h3>
              <dl className="space-y-2.5">
                <div className="flex justify-between text-sm">
                  <dt className="text-zinc-500">Category</dt>
                  <dd className="text-zinc-200 font-medium capitalize">{agent.category || 'General'}</dd>
                </div>
                <div className="flex justify-between text-sm">
                  <dt className="text-zinc-500">Type</dt>
                  <dd className="text-zinc-200 font-medium capitalize">{agent.agent_type}</dd>
                </div>
                <div className="flex justify-between text-sm">
                  <dt className="text-zinc-500">Capabilities</dt>
                  <dd className="text-zinc-200 font-medium">{capabilities.length}</dd>
                </div>
                <div className="flex justify-between text-sm">
                  <dt className="text-zinc-500">Connections</dt>
                  <dd className="text-zinc-200 font-medium">{connections.length}</dd>
                </div>
              </dl>
            </div>

            {/* Made by */}
            <div className="rounded-2xl border border-border bg-card p-5 flex items-center gap-3">
              <Sparkles className="w-4 h-4 text-zinc-500 shrink-0" />
              <div>
                <p className="text-[13px] text-zinc-400">Built by</p>
                <p className="text-[14px] text-zinc-200 font-medium">OnlyFounders</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
