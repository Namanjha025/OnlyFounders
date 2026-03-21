import { ChevronRight, MessageCircle } from 'lucide-react'
import { Link } from 'react-router-dom'

import { cn } from '@/lib/utils'
import { marketplaceSections, type MarketplaceAgent } from '@/data/marketplaceMock'

function formatInteractions(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}m`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}k`
  return String(n)
}

function avatarGradient(seed: string): string {
  let h = 0
  for (let i = 0; i < seed.length; i++) h = (h + seed.charCodeAt(i) * (i + 1)) % 360
  const h2 = (h + 40) % 360
  return `linear-gradient(135deg, hsl(${h} 45% 32%), hsl(${h2} 40% 22%))`
}

function titleInitials(title: string): string {
  const words = title.match(/[A-Za-z]+/g) ?? []
  return words
    .slice(0, 2)
    .map((w) => w[0])
    .join('')
    .toUpperCase() || 'AI'
}

function AgentCard({ agent }: { agent: MarketplaceAgent }) {
  const initials = titleInitials(agent.name)

  return (
    <Link
      to={`/marketplace/${agent.id}`}
      className={cn(
        'group flex min-w-[220px] max-w-[280px] sm:min-w-[240px] flex-shrink-0 gap-3 rounded-2xl bg-[#1a1a1a] p-3 pr-3',
        'border border-white/[0.06] transition-colors hover:bg-[#222222] hover:border-white/[0.1]',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/20'
      )}
    >
      <div
        className="h-[72px] w-[72px] shrink-0 overflow-hidden rounded-xl bg-zinc-800"
        style={{ background: avatarGradient(agent.avatarSeed) }}
      >
        <div className="flex h-full w-full items-center justify-center text-lg font-semibold text-white/90">
          {initials}
        </div>
      </div>
      <div className="flex min-w-0 flex-1 flex-col justify-between py-0.5">
        <div>
          <p className="text-[15px] font-semibold leading-tight text-white group-hover:text-white">{agent.name}</p>
          <p className="mt-0.5 text-[12px] text-zinc-500">By @{agent.creatorHandle}</p>
          <p className="mt-1.5 line-clamp-2 text-[13px] leading-snug text-zinc-300">{agent.description}</p>
        </div>
        <div className="mt-2 flex items-center gap-1 text-[12px] text-zinc-500">
          <MessageCircle className="h-3.5 w-3.5 shrink-0" strokeWidth={2} />
          <span>{formatInteractions(agent.interactionCount)}</span>
        </div>
      </div>
    </Link>
  )
}

function SectionRow({ title, agents }: { title: string; agents: MarketplaceAgent[] }) {
  return (
    <section className="mb-10">
      <div className="mb-3 flex items-center justify-between px-1">
        <h2 className="text-lg font-semibold tracking-tight text-white">{title}</h2>
        <button
          type="button"
          className="flex items-center gap-0.5 text-zinc-500 transition-colors hover:text-zinc-300"
          aria-label={`More in ${title}`}
        >
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>
      <div className="flex gap-3 overflow-x-auto pb-1 [-ms-overflow-style:none] [scrollbar-width:thin] [&::-webkit-scrollbar]:h-1.5 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-zinc-700 [&::-webkit-scrollbar-track]:bg-transparent">
        {agents.map((a) => (
          <AgentCard key={a.id} agent={a} />
        ))}
      </div>
    </section>
  )
}

export function Marketplace() {
  return (
    <div className="animate-fade-in -m-8 min-h-screen bg-black text-white">
      <div className="mx-auto max-w-[1400px] px-6 py-8 pb-16 sm:px-8">
        <header className="mb-10">
          <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">TwinVerse</h1>
          <p className="mt-1 max-w-xl text-[15px] text-zinc-400">
            Browse AI Twins — mentors, specialists, and tools for your startup. Character-style cards; chat wiring
            comes next.
          </p>
        </header>

        {marketplaceSections.map((section) => (
          <SectionRow key={section.title} title={section.title} agents={section.agents} />
        ))}
      </div>
    </div>
  )
}
