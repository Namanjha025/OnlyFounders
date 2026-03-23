import { useState, useEffect } from 'react'
import { ChevronRight, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { agents as agentsApi, type AgentOut } from '@/lib/api'
import { resolveIcon } from '@/lib/icons'
import { AgentProfileModal } from '@/components/AgentProfileModal'

export function Agents() {
  const [agentList, setAgentList] = useState<AgentOut[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedAgent, setSelectedAgent] = useState<AgentOut | null>(null)

  useEffect(() => {
    agentsApi.list().then(setAgentList).catch(() => {}).finally(() => setLoading(false))
  }, [])

  const categories = [...new Set(agentList.map((a) => a.category).filter(Boolean))]

  return (
    <div className="animate-fade-in -m-8 min-h-screen flex flex-col bg-[#050507]">
      <div className="flex-1 flex flex-col px-6 pt-10 pb-10">
        <div className="max-w-4xl mx-auto w-full">
          <h1 className="text-2xl font-semibold text-foreground tracking-tight">Agents</h1>
          <p className="text-[15px] text-muted-foreground mt-1">
            Pre-built agents that join your workspace and get to work. Enroll to add them.
          </p>

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-5 h-5 text-zinc-500 animate-spin" />
            </div>
          ) : (
            categories.map((category) => {
              const filtered = agentList.filter((a) => a.category === category)
              return (
                <div key={category} className="mt-10">
                  <h2 className="text-[13px] uppercase tracking-wider text-zinc-500 font-medium mb-4">{category}</h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {filtered.map((agent) => {
                      const Icon = resolveIcon(agent.icon)
                      return (
                        <button
                          key={agent.id}
                          onClick={() => setSelectedAgent(agent)}
                          className={cn(
                            'group rounded-xl border border-white/[0.06] bg-white/[0.02] p-4 transition-all text-left',
                            'hover:bg-white/[0.05] hover:border-white/[0.12] cursor-pointer'
                          )}
                        >
                          <div className="flex items-start gap-3">
                            <div
                              className="flex items-center justify-center w-10 h-10 rounded-lg shrink-0 transition-colors"
                              style={{ backgroundColor: agent.color ? `${agent.color}15` : 'rgba(255,255,255,0.06)' }}
                            >
                              <Icon className="w-5 h-5 transition-colors" style={{ color: agent.color || '#999' }} />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-[15px] font-medium text-foreground leading-snug">{agent.name}</p>
                              <p className="text-[12px] text-muted-foreground mt-1 leading-relaxed">{agent.description}</p>
                              <div className="flex flex-wrap gap-1.5 mt-3">
                                {(agent.capabilities ?? []).map((cap) => (
                                  <span key={cap} className="text-[11px] px-2 py-0.5 rounded-full bg-white/[0.05] text-zinc-400 font-medium">{cap}</span>
                                ))}
                              </div>
                            </div>
                            <ChevronRight className="w-5 h-5 text-zinc-700 shrink-0 mt-1 group-hover:text-zinc-400 transition-colors" />
                          </div>
                        </button>
                      )
                    })}
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>

      {selectedAgent && (
        <AgentProfileModal
          agent={{
            id: selectedAgent.id,
            name: selectedAgent.name,
            icon: resolveIcon(selectedAgent.icon),
            color: selectedAgent.color || '#999',
            category: selectedAgent.category || 'General',
            description: selectedAgent.description || '',
            capabilities: selectedAgent.capabilities ?? [],
            instructions: selectedAgent.instructions ?? [],
            connections: selectedAgent.connections ?? [],
          }}
          open={true}
          onClose={() => setSelectedAgent(null)}
        />
      )}
    </div>
  )
}
