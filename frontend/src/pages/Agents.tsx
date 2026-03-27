import { useState, useEffect } from 'react'
import { Search, Bot, SlidersHorizontal, ChevronDown, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { agents as agentsApi, team as teamApi, type AgentOut, type TeamAgentOut } from '@/lib/api'
import { resolveIcon } from '@/lib/icons'
import { avatarGradient, scoreToColor, EntityCard, CardSkeleton } from '@/components/shared'

const SORT_OPTIONS = [
  { value: 'name', label: 'Name' },
  { value: 'category', label: 'Category' },
  { value: 'capabilities', label: 'Most Capable' },
]

function AgentCard({ agent, isHired }: { agent: AgentOut; isHired: boolean }) {
  const Icon = resolveIcon(agent.icon)
  const capCount = agent.capabilities?.length ?? 0
  const capScore = Math.min(capCount / 10, 1)

  return (
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
      badge={isHired}
    />
  )
}

export function Agents() {
  const [agentList, setAgentList] = useState<AgentOut[]>([])
  const [teamList, setTeamList] = useState<TeamAgentOut[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [activeTab, setActiveTab] = useState('')
  const [sortBy, setSortBy] = useState('name')
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    agentsApi.list()
      .then((a) => setAgentList(a))
      .catch(() => {})
    teamApi.list()
      .then((t) => setTeamList(t))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const hiredIds = new Set(teamList.map((t) => t.agent_id))

  const categories = ['', ...Array.from(new Set(agentList.map((a) => a.category).filter(Boolean)))]
  const categoryCounts = agentList.reduce<Record<string, number>>((acc, a) => {
    const cat = a.category || ''
    acc[cat] = (acc[cat] || 0) + 1
    return acc
  }, {})

  let filtered = agentList.filter((a) => {
    if (activeTab && a.category !== activeTab) return false
    if (showFilters && !hiredIds.has(a.id)) return false
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

  if (sortBy === 'name') filtered.sort((a, b) => a.name.localeCompare(b.name))
  else if (sortBy === 'category') filtered.sort((a, b) => (a.category || '').localeCompare(b.category || ''))
  else if (sortBy === 'capabilities') filtered.sort((a, b) => (b.capabilities?.length ?? 0) - (a.capabilities?.length ?? 0))

  const activeFilterCount = (search ? 1 : 0) + (showFilters ? 1 : 0)
  const clearFilters = () => { setSearch(''); setShowFilters(false); setActiveTab('') }
  const handleSearch = (e: React.FormEvent) => { e.preventDefault() }

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

        {/* Search bar */}
        <form onSubmit={handleSearch} className="flex gap-2 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by name, skill, or capability..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-card border border-border rounded-xl pl-10 pr-4 py-3 text-[15px] text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-white/20 transition"
            />
          </div>
          <button type="submit"
            className="bg-white text-black px-6 py-3 rounded-xl text-[14px] font-semibold hover:bg-zinc-200 transition">
            Search
          </button>
          <button type="button" onClick={() => setShowFilters(!showFilters)}
            className={cn('p-3 rounded-xl border transition relative',
              showFilters ? 'bg-white/[0.06] border-white/20 text-foreground' : 'border-border text-muted-foreground hover:text-foreground')}>
            <SlidersHorizontal className="w-4 h-4" />
            {activeFilterCount > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-white text-black text-[9px] font-bold rounded-full flex items-center justify-center">
                {activeFilterCount}
              </span>
            )}
          </button>
        </form>

        {/* Tabs + Sort */}
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

          <div className="flex items-center gap-3">
            {activeFilterCount > 0 && (
              <button onClick={clearFilters} className="text-[12px] text-muted-foreground hover:text-foreground flex items-center gap-1">
                <X className="w-3 h-3" /> Clear filters
              </button>
            )}
            <div className="relative">
              <select value={sortBy} onChange={e => setSortBy(e.target.value)}
                className="appearance-none bg-card border border-border rounded-lg px-3 py-1.5 pr-8 text-[13px] text-foreground focus:outline-none focus:border-white/20 cursor-pointer">
                {SORT_OPTIONS.map(o => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
            </div>
            <span className="text-[13px] text-muted-foreground">{filtered.length} agents</span>
          </div>
        </div>

        {/* Grid */}
        <div className="flex-1">
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
              {activeFilterCount > 0 && (
                <button onClick={clearFilters} className="mt-3 text-[13px] text-muted-foreground hover:text-foreground underline">
                  Clear all filters
                </button>
              )}
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {filtered.map((agent) => (
                <AgentCard key={agent.id} agent={agent} isHired={hiredIds.has(agent.id)} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
