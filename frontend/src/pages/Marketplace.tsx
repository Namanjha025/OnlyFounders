import { useEffect, useState, useCallback } from 'react'
import { Search, SlidersHorizontal, Sparkles, ChevronDown, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { marketplace, type MarketplaceProfile, type FacetResponse } from '@/lib/api'
import { avatarGradient, nameInitials, scoreToColor, EntityCard, CardSkeleton } from '@/components/shared'

const TABS = [
  { key: '', label: 'All' },
  { key: 'professional', label: 'Professionals' },
  { key: 'advisor', label: 'Advisors' },
  { key: 'founder', label: 'Founders' },
]

const SORT_OPTIONS = [
  { value: 'score', label: 'Top Score' },
  { value: 'newest', label: 'Newest' },
  { value: 'relevance', label: 'Relevance' },
  { value: 'rate_low', label: 'Rate: Low→High' },
  { value: 'rate_high', label: 'Rate: High→Low' },
]

function ProfileCard({ profile }: { profile: MarketplaceProfile }) {
  return (
    <EntityCard
      to={`/marketplace/${profile.id}`}
      avatarContent={
        <div className="w-full h-full flex items-center justify-center text-lg font-semibold text-white/90"
          style={{ background: avatarGradient(profile.display_name || profile.headline || profile.id) }}>
          {nameInitials(profile.display_name || profile.headline)}
        </div>
      }
      ringProgress={Math.min(profile.profile_score, 100) / 100}
      ringColor={scoreToColor(profile.profile_score)}
      name={profile.display_name || profile.headline || 'Untitled'}
      subtitle={profile.display_name ? (profile.headline || null) : null}
      type={profile.profile_type}
      description={profile.bio}
      tags={profile.skills ?? undefined}
    />
  )
}

/* ── Filter Sidebar ────────────────────────────────────────────── */

function FilterSidebar({
  facets,
  filters,
  setFilter,
  activeTab,
}: {
  facets: FacetResponse | null
  filters: Record<string, string>
  setFilter: (key: string, value: string) => void
  activeTab: string
}) {
  if (!facets) return null

  return (
    <div className="space-y-5">
      {facets.skills.length > 0 && (
        <div>
          <h4 className="text-[12px] font-semibold text-muted-foreground uppercase tracking-wider mb-2">Skills</h4>
          <div className="space-y-1 max-h-48 overflow-y-auto">
            {facets.skills.map(s => (
              <button key={s.value} onClick={() => setFilter('skills', s.value)}
                className={cn('flex items-center justify-between w-full text-left text-[13px] px-2 py-1 rounded-lg transition',
                  filters.skills === s.value ? 'bg-white/[0.08] text-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-white/[0.03]')}>
                <span>{s.value}</span>
                <span className="text-[11px] text-muted-foreground">{s.count}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {(activeTab === '' || activeTab === 'professional') && facets.availability.length > 0 && (
        <div>
          <h4 className="text-[12px] font-semibold text-muted-foreground uppercase tracking-wider mb-2">Availability</h4>
          <div className="space-y-1">
            {facets.availability.map(a => (
              <button key={a.value} onClick={() => setFilter('availability', a.value)}
                className={cn('flex items-center justify-between w-full text-left text-[13px] px-2 py-1 rounded-lg transition',
                  filters.availability === a.value ? 'bg-white/[0.08] text-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-white/[0.03]')}>
                <span className="capitalize">{a.value.replace(/_/g, ' ')}</span>
                <span className="text-[11px] text-muted-foreground">{a.count}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {(activeTab === '' || activeTab === 'professional') && facets.hourly_rate_ranges.length > 0 && (
        <div>
          <h4 className="text-[12px] font-semibold text-muted-foreground uppercase tracking-wider mb-2">Hourly Rate</h4>
          <div className="space-y-1">
            {facets.hourly_rate_ranges.map(r => (
              <button key={r.value} onClick={() => {
                const [min, max] = r.value.replace('+', '-9999').split('-')
                setFilter('min_rate', min)
                if (max !== '9999') setFilter('max_rate', max)
              }}
                className="flex items-center justify-between w-full text-left text-[13px] px-2 py-1 rounded-lg text-muted-foreground hover:text-foreground hover:bg-white/[0.03] transition">
                <span>${r.value}</span>
                <span className="text-[11px] text-muted-foreground">{r.count}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {facets.locations.length > 0 && (
        <div>
          <h4 className="text-[12px] font-semibold text-muted-foreground uppercase tracking-wider mb-2">Location</h4>
          <div className="space-y-1 max-h-36 overflow-y-auto">
            {facets.locations.map(l => (
              <button key={l.value} onClick={() => setFilter('location', l.value)}
                className={cn('flex items-center justify-between w-full text-left text-[13px] px-2 py-1 rounded-lg transition',
                  filters.location === l.value ? 'bg-white/[0.08] text-foreground' : 'text-muted-foreground hover:text-foreground hover:bg-white/[0.03]')}>
                <span>{l.value}</span>
                <span className="text-[11px] text-muted-foreground">{l.count}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

/* ── Main Page ─────────────────────────────────────────────────── */

export function Marketplace() {
  const [profiles, setProfiles] = useState<MarketplaceProfile[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [facets, setFacets] = useState<FacetResponse | null>(null)

  const [search, setSearch] = useState('')
  const [activeTab, setActiveTab] = useState('')
  const [sortBy, setSortBy] = useState('score')
  const [showFilters, setShowFilters] = useState(false)
  const [filters, setFilters] = useState<Record<string, string>>({})

  const setFilter = useCallback((key: string, value: string) => {
    setFilters(prev => {
      if (prev[key] === value) {
        const next = { ...prev }
        delete next[key]
        return next
      }
      return { ...prev, [key]: value }
    })
  }, [])

  const clearFilters = () => { setFilters({}); setSearch('') }

  const activeFilterCount = Object.keys(filters).length + (search ? 1 : 0)

  const fetchProfiles = useCallback(async () => {
    setLoading(true); setError('')
    try {
      const params: Record<string, string> = {
        sort_by: sortBy,
        include_facets: 'true',
      }
      if (search) params.q = search
      if (activeTab) params.profile_type = activeTab
      Object.entries(filters).forEach(([k, v]) => { params[k] = v })

      let result
      if (search && !activeTab) {
        params.q = search
        result = await marketplace.search(params)
      } else if (activeTab === 'professional') {
        result = await marketplace.discoverProfessionals(params)
      } else if (activeTab === 'advisor') {
        result = await marketplace.discoverAdvisors(params)
      } else if (activeTab === 'founder') {
        result = await marketplace.discoverFounders(params)
      } else {
        result = await marketplace.discover(params)
      }

      setProfiles(result.items)
      setTotal(result.total)
      if (result.facets) setFacets(result.facets)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load')
    } finally {
      setLoading(false)
    }
  }, [search, activeTab, sortBy, filters])

  useEffect(() => { fetchProfiles() }, [fetchProfiles])

  const handleSearch = (e: React.FormEvent) => { e.preventDefault(); fetchProfiles() }

  return (
    <div className="animate-fade-in -m-8 min-h-screen bg-[#050507]">
      <div className="mx-auto max-w-[1400px] px-6 py-8 pb-16 sm:px-8">
        {/* Header */}
        <header className="mb-6">
          <div className="flex items-center gap-2 mb-1">
            <Sparkles className="w-5 h-5 text-muted-foreground" />
            <h1 className="text-2xl font-semibold text-foreground tracking-tight">TwinVerse</h1>
          </div>
          <p className="mt-1 max-w-xl text-[15px] text-muted-foreground">
            Discover professionals, advisors, and founders.
          </p>
        </header>

        {/* Search bar */}
        <form onSubmit={handleSearch} className="flex gap-2 mb-4">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input type="text" placeholder="Search by name, skill, or keyword..."
              value={search} onChange={e => setSearch(e.target.value)}
              className="w-full bg-card border border-border rounded-xl pl-10 pr-4 py-3 text-[15px] text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-white/20 transition" />
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
          <div className="flex gap-1">
            {TABS.map(tab => (
              <button key={tab.key} onClick={() => setActiveTab(tab.key)}
                className={cn('text-[13px] px-4 py-2 rounded-full font-medium transition',
                  activeTab === tab.key
                    ? 'bg-white text-black'
                    : 'text-muted-foreground hover:text-foreground hover:bg-white/[0.04]')}>
                {tab.label}
                {facets && tab.key && (
                  <span className="ml-1 text-[11px] opacity-60">
                    {facets.profile_types.find(f => f.value === tab.key)?.count ?? 0}
                  </span>
                )}
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
            <span className="text-[13px] text-muted-foreground">{total} results</span>
          </div>
        </div>

        {error && <div className="text-red-400 text-[14px] bg-red-500/10 border border-red-500/15 rounded-xl p-4 mb-6">{error}</div>}

        {/* Content: Filters + Grid */}
        <div className={cn('flex gap-6', showFilters ? '' : '')}>
          {showFilters && (
            <aside className="w-56 shrink-0">
              <div className="sticky top-20 bg-card border border-border rounded-2xl p-4">
                <h3 className="text-[13px] font-semibold text-foreground mb-4">Filters</h3>
                <FilterSidebar facets={facets} filters={filters} setFilter={setFilter} activeTab={activeTab} />
              </div>
            </aside>
          )}

          <div className="flex-1">
            {loading ? (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {Array.from({ length: 8 }).map((_, i) => <CardSkeleton key={i} />)}
              </div>
            ) : profiles.length === 0 ? (
              <div className="text-center py-20">
                <div className="w-16 h-16 rounded-2xl bg-secondary flex items-center justify-center mx-auto mb-4">
                  <Search className="w-7 h-7 text-muted-foreground" />
                </div>
                <p className="text-foreground font-medium">No profiles found</p>
                <p className="text-[14px] text-muted-foreground mt-1">Try different search terms or filters.</p>
                {activeFilterCount > 0 && (
                  <button onClick={clearFilters} className="mt-3 text-[13px] text-muted-foreground hover:text-foreground underline">
                    Clear all filters
                  </button>
                )}
              </div>
            ) : (
              <div className={cn(
                'grid gap-4',
                showFilters ? 'sm:grid-cols-2 lg:grid-cols-3' : 'sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
              )}>
                {profiles.map(p => <ProfileCard key={p.id} profile={p} />)}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
