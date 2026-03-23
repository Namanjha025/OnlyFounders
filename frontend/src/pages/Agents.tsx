import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Search, Bot, Loader2, Check } from 'lucide-react'
import { cn } from '@/lib/utils'
import { agents as agentsApi, team as teamApi, type AgentOut, type TeamAgentOut } from '@/lib/api'
import { resolveIcon } from '@/lib/icons'

function AgentCard({
  agent, isHired,
}: {
  agent: AgentOut
  isHired: boolean
}) {
  const Icon = resolveIcon(agent.icon)

  return (
    <Link
      to={`/agents/${agent.id}`}
      className={cn(
        'group flex flex-col items-center rounded-2xl bg-card p-6',
        'border border-border transition-all duration-200 text-center',
        'hover:border-white/[0.12] hover:bg-white/[0.03]',
      )}
    >
      <div className="relative mb-3">
        <div
          className="w-16 h-16 rounded-2xl flex items-center justify-center"
          style={{ backgroundColor: agent.color ? `${agent.color}15` : 'rgba(255,255,255,0.06)' }}
        >
          <Icon className="w-7 h-7" style={{ color: agent.color || '#999' }} />
        </div>
        {isHired && (
          <div className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center ring-2 ring-[#050507]">
            <Check className="w-3 h-3 text-white" strokeWidth={3} />
          </div>
        )}
      </div>

      <p className="text-[15px] font-semibold text-foreground leading-tight mb-0.5">{agent.name}</p>
      <p className="text-[12px] text-muted-foreground capitalize">{agent.category || 'General'}</p>

      {agent.description && (
        <p className="text-[13px] text-muted-foreground text-center line-clamp-2 leading-relaxed mt-2">
          {agent.description}
        </p>
      )}

      {agent.capabilities && agent.capabilities.length > 0 && (
        <div className="flex flex-wrap justify-center gap-1 mt-3">
          {agent.capabilities.slice(0, 3).map((cap) => (
            <span key={cap} className="text-[11px] text-muted-foreground bg-secondary px-2 py-0.5 rounded-full">{cap}</span>
          ))}
          {agent.capabilities.length > 3 && (
            <span className="text-[11px] text-muted-foreground">+{agent.capabilities.length - 3}</span>
          )}
        </div>
      )}
    </Link>
  )
}

function CardSkeleton() {
  return (
    <div className="rounded-2xl bg-card border border-border p-6 flex flex-col items-center">
      <div className="w-16 h-16 rounded-2xl bg-secondary animate-pulse mb-3" />
      <div className="h-4 w-28 bg-secondary rounded animate-pulse mb-2" />
      <div className="h-3 w-16 bg-secondary rounded animate-pulse mb-3" />
      <div className="h-10 w-full bg-secondary rounded animate-pulse" />
    </div>
  )
}

export function Agents() {
  const [agentList, setAgentList] = useState<AgentOut[]>([])
  const [teamList, setTeamList] = useState<TeamAgentOut[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [activeTab, setActiveTab] = useState('')

  useEffect(() => {
    Promise.all([agentsApi.list(), teamApi.list()])
      .then(([a, t]) => { setAgentList(a); setTeamList(t) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const hiredIds = new Set(teamList.map((t) => t.agent_id))

  const categories = ['', ...new Set(agentList.map((a) => a.category).filter(Boolean))]
  const categoryCounts = agentList.reduce<Record<string, number>>((acc, a) => {
    const cat = a.category || ''
    acc[cat] = (acc[cat] || 0) + 1
    return acc
  }, {})

  const filtered = agentList.filter((a) => {
    if (activeTab && a.category !== activeTab) return false
    if (search) {
      const q = search.toLowerCase()
      const match =
        a.name.toLowerCase().includes(q) ||
        (a.description || '').toLowerCase().includes(q) ||
        (a.category || '').toLowerCase().includes(q) ||
        (a.capabilities || []).some((c) => c.toLowerCase().includes(q))
      if (!match) return false
    }
    return true
  })

  return (
    <div className="animate-fade-in -m-8 min-h-screen bg-[#050507]">
      <div className="mx-auto max-w-[1400px] px-6 py-8 pb-16 sm:px-8">
        {/* Header */}
        <header className="mb-6">
          <div className="flex items-center gap-2 mb-1">
            <Bot className="w-5 h-5 text-muted-foreground" />
            <h1 className="text-2xl font-semibold text-foreground tracking-tight">Agents</h1>
          </div>
          <p className="mt-1 max-w-xl text-[15px] text-muted-foreground">
            Pre-built AI agents that join your team and work on cases. Hire them to get started.
          </p>
        </header>

        {/* Search */}
        <div className="flex gap-2 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search agents by name, skill, or capability..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-card border border-border rounded-xl pl-10 pr-4 py-3 text-[15px] text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-white/20 transition"
            />
          </div>
        </div>

        {/* Tabs */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex gap-1 flex-wrap">
            {categories.map((cat) => (
              <button
                key={cat || '__all'}
                onClick={() => setActiveTab(cat)}
                className={cn(
                  'text-[13px] px-4 py-2 rounded-full font-medium transition',
                  activeTab === cat
                    ? 'bg-white text-black'
                    : 'text-muted-foreground hover:text-foreground hover:bg-white/[0.04]'
                )}
              >
                {cat || 'All'}
                <span className="ml-1 text-[11px] opacity-60">
                  {cat ? (categoryCounts[cat] || 0) : agentList.length}
                </span>
              </button>
            ))}
          </div>
          <span className="text-[13px] text-muted-foreground">{filtered.length} agents</span>
        </div>

        {/* Grid */}
        {loading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {Array.from({ length: 8 }).map((_, i) => <CardSkeleton key={i} />)}
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-20">
            <div className="w-16 h-16 rounded-2xl bg-secondary flex items-center justify-center mx-auto mb-4">
              <Search className="w-7 h-7 text-muted-foreground" />
            </div>
            <p className="text-foreground font-medium">No agents found</p>
            <p className="text-[14px] text-muted-foreground mt-1">Try different search terms or categories.</p>
            {(search || activeTab) && (
              <button onClick={() => { setSearch(''); setActiveTab('') }} className="mt-3 text-[13px] text-muted-foreground hover:text-foreground underline">
                Clear filters
              </button>
            )}
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {filtered.map((agent) => (
              <AgentCard
                key={agent.id}
                agent={agent}
                isHired={hiredIds.has(agent.id)}
              />
            ))}
          </div>
        )}
      </div>

    </div>
  )
}
