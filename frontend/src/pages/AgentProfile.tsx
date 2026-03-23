import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Bot, CheckCircle2, Plug, Heart, Briefcase, Users, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { agents as agentsApi, team as teamApi, type AgentOut, type TeamAgentOut } from '@/lib/api'
import { resolveIcon } from '@/lib/icons'

function iconGradient(seed: string, color?: string | null): string {
  if (color) {
    const r = parseInt(color.slice(1, 3), 16) || 80
    const g = parseInt(color.slice(3, 5), 16) || 80
    const b = parseInt(color.slice(5, 7), 16) || 80
    return `linear-gradient(135deg, rgba(${r},${g},${b},0.35), rgba(${r},${g},${b},0.15))`
  }
  let h = 0
  for (let i = 0; i < seed.length; i++) h = (h + seed.charCodeAt(i) * (i + 1)) % 360
  return `linear-gradient(135deg, hsl(${h} 50% 35%), hsl(${(h + 50) % 360} 45% 25%))`
}

function CapabilityRing({ count, color }: { count: number; color: string }) {
  const r = 40
  const circ = 2 * Math.PI * r
  const score = Math.min(count / 10, 1)
  const offset = circ - score * circ
  return (
    <div className="relative w-24 h-24">
      <svg className="w-24 h-24 -rotate-90" viewBox="0 0 96 96">
        <circle cx="48" cy="48" r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="5" />
        <circle cx="48" cy="48" r={r} fill="none" stroke={color}
          strokeWidth="5" strokeLinecap="round"
          strokeDasharray={circ} strokeDashoffset={offset}
          className="transition-all duration-1000" />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-bold text-white">{count}</span>
        <span className="text-[10px] text-zinc-500">skills</span>
      </div>
    </div>
  )
}

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
      <div className="w-8 h-8 border-2 border-white/30 border-t-zinc-300 rounded-full animate-spin" />
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
      {/* Top bar — same as marketplace */}
      <div className="border-b border-border bg-background/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-3 flex items-center justify-between">
          <Link to="/agents" className="flex items-center gap-2 text-sm text-zinc-400 hover:text-zinc-300 transition">
            <ArrowLeft className="w-4 h-4" /> Back to agents
          </Link>
          {!isHired && (
            <button
              onClick={handleHire}
              className="flex items-center gap-2 bg-white text-black px-4 py-1.5 rounded-lg text-sm font-semibold hover:bg-zinc-300 transition"
            >
              <Users className="w-3.5 h-3.5" /> Hire to Team
            </button>
          )}
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-6">

          {/* ── Left Column: Main Profile ──────────────────────── */}
          <div className="space-y-6">
            {/* Avatar + Name card — matches marketplace pattern */}
            <div className="rounded-2xl border border-border bg-card p-8">
              <div className="flex flex-col items-center">
                <div className="w-28 h-28 rounded-full border-[3px] p-1" style={{ borderColor: `${agent.color || '#666'}60` }}>
                  <div
                    className="w-full h-full rounded-full flex items-center justify-center"
                    style={{ background: iconGradient(agent.name, agent.color) }}
                  >
                    <Icon className="w-12 h-12" style={{ color: agent.color || '#ccc' }} />
                  </div>
                </div>
                <h1 className="text-2xl font-semibold mt-4">{agent.name}</h1>
                <p className="text-sm text-zinc-300 capitalize mt-1">{agent.category || 'General'}</p>
                {isHired && (
                  <p className="flex items-center gap-1 text-sm text-emerald-400 mt-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> On your team
                  </p>
                )}
              </div>
            </div>

            {/* About + Capabilities (like About + Skills in marketplace) */}
            {(agent.description || capabilities.length > 0) && (
              <div className="rounded-2xl border border-border bg-card p-6">
                <h2 className="font-semibold text-[15px] text-foreground mb-3">About</h2>
                {agent.description && (
                  <div className="border-l-2 border-white/30 pl-4 mb-4">
                    <p className="text-sm text-zinc-300 leading-relaxed whitespace-pre-line">{agent.description}</p>
                  </div>
                )}
                {capabilities.length > 0 && (
                  <div>
                    <p className="text-[11px] uppercase tracking-wider text-zinc-500 mb-2">Capabilities</p>
                    <div className="flex flex-wrap gap-1.5">
                      {capabilities.map((cap) => (
                        <span key={cap} className="text-xs text-emerald-300/80 bg-emerald-500/10 border border-emerald-500/15 px-2.5 py-1 rounded-full">
                          {cap}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Instructions (like "How I Can Help" in marketplace) */}
            {instructions.length > 0 && (
              <div className="rounded-2xl border border-border bg-card p-6">
                <h2 className="flex items-center gap-2 font-semibold text-[15px] text-foreground mb-3">
                  <Heart className="w-4 h-4 text-zinc-400" />
                  What This Agent Does
                </h2>
                {instructions.map((instruction, i) => (
                  <div key={i} className="border-l-2 border-white/30 pl-4 mb-3 last:mb-0">
                    <p className="text-sm text-zinc-400">{instruction}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Connections (like Professional Details in marketplace) */}
            {connections.length > 0 && (
              <div className="rounded-2xl border border-border bg-card p-6">
                <h2 className="flex items-center gap-2 font-semibold text-[15px] text-foreground mb-4">
                  <Briefcase className="w-4 h-4 text-zinc-300" />
                  Connections & Integrations
                </h2>
                <div className="grid grid-cols-2 gap-4">
                  {connections.map((conn) => (
                    <div key={conn.name}>
                      <p className="text-[11px] uppercase tracking-wider text-zinc-500 mb-1">
                        Integration
                      </p>
                      <p className="text-sm text-zinc-200">{conn.name}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* ── Right Column: Sidebar ──────────────────────────── */}
          <div className="space-y-4">
            {/* Hire card (like Connect card in marketplace) */}
            <div className="rounded-2xl border border-border bg-card p-5">
              <h3 className="font-semibold text-[15px] text-foreground mb-3">Add to Team</h3>
              <p className="text-xs text-zinc-500 mb-3">
                {isHired
                  ? 'This agent is on your team. Assign it to cases anytime.'
                  : 'Hire this agent to your team — then assign it to any case.'}
              </p>
              <button
                onClick={handleHire}
                disabled={isHired}
                className={cn(
                  'w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium transition',
                  isHired
                    ? 'bg-white/[0.06] text-zinc-500 cursor-default'
                    : 'border border-white/20 text-zinc-300 hover:bg-white/5 hover:border-white/30'
                )}
              >
                <Users className="w-4 h-4" /> {isHired ? 'Already on Team' : 'Hire to Team'}
              </button>
            </div>

            {/* Quick Info (matches marketplace) */}
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

            {/* Capability ring (matches ScoreRing in marketplace) */}
            <div className="rounded-2xl border border-border bg-card p-5 flex flex-col items-center">
              <CapabilityRing count={capabilities.length} color={agent.color || '#666'} />
              <p className="text-xs text-zinc-500 mt-3">
                {capabilities.length >= 8 ? 'Highly Capable' :
                 capabilities.length >= 5 ? 'Well-Rounded' :
                 capabilities.length >= 3 ? 'Focused Agent' : 'Specialized'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
