import { X, CheckCircle2, Plug, Bot, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils'

interface AgentProfile {
  id: string
  name: string
  icon: React.ComponentType<{ className?: string; style?: React.CSSProperties }>
  color: string
  category: string
  description: string
  capabilities: string[]
  instructions?: string[]
  connections?: { name: string; icon?: string }[]
}

interface Props {
  agent: AgentProfile | null
  open: boolean
  onClose: () => void
  onHire?: (agentId: string) => void
  isHired?: boolean
}

export function AgentProfileModal({ agent, open, onClose, onHire, isHired }: Props) {
  if (!open || !agent) return null

  const Icon = agent.icon

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

      {/* Modal */}
      <div className="relative w-full max-w-2xl max-h-[85vh] overflow-y-auto rounded-2xl border border-white/[0.08] bg-[#0c0c10] shadow-2xl shadow-black/50 mx-4">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 text-zinc-500 hover:text-white hover:bg-white/[0.06] rounded-lg transition-colors z-10"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="p-8 pb-0">
          <div className="flex items-center gap-2 text-[12px] text-zinc-500 mb-4">
            <Sparkles className="w-3.5 h-3.5" />
            <span>by OnlyFounders</span>
          </div>

          <div className="flex items-start gap-4">
            <div className="flex-1">
              <h2 className="text-2xl font-semibold text-foreground">{agent.name}</h2>
              <p className="text-[15px] text-zinc-400 mt-2 leading-relaxed">{agent.description}</p>

              {/* Category + agent type badge */}
              <div className="flex items-center gap-2 mt-4">
                <span className="text-[12px] px-2.5 py-1 rounded-full font-medium border"
                  style={{ backgroundColor: `${agent.color}10`, color: agent.color, borderColor: `${agent.color}30` }}>
                  {agent.category}
                </span>
                <span className="text-[12px] px-2.5 py-1 rounded-full bg-white/[0.05] text-zinc-400 font-medium border border-white/[0.08]">
                  Platform Agent
                </span>
              </div>
            </div>

            {/* Agent icon large */}
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center shrink-0"
              style={{ backgroundColor: `${agent.color}15` }}
            >
              <Icon className="w-8 h-8" style={{ color: agent.color }} />
            </div>
          </div>
        </div>

        {/* Capabilities */}
        <div className="px-8 pt-8">
          <h3 className="text-[13px] uppercase tracking-wider text-zinc-500 font-medium mb-3 flex items-center gap-2">
            <Bot className="w-3.5 h-3.5" />
            Capabilities
          </h3>
          <div className="flex flex-wrap gap-2">
            {agent.capabilities.map((cap) => (
              <span
                key={cap}
                className="text-[13px] px-3 py-1.5 rounded-lg bg-white/[0.04] text-zinc-300 font-medium border border-white/[0.06]"
              >
                {cap}
              </span>
            ))}
          </div>
        </div>

        {/* Instructions */}
        {agent.instructions && agent.instructions.length > 0 && (
          <div className="px-8 pt-8">
            <h3 className="text-[13px] uppercase tracking-wider text-zinc-500 font-medium mb-3 flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Agent Instructions
            </h3>
            <div className="space-y-2.5">
              {agent.instructions.map((instruction, i) => (
                <div key={i} className="flex items-start gap-2.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                  <p className="text-[14px] text-zinc-300 leading-relaxed">{instruction}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Connections */}
        {agent.connections && agent.connections.length > 0 && (
          <div className="px-8 pt-8">
            <h3 className="text-[13px] uppercase tracking-wider text-zinc-500 font-medium mb-3 flex items-center gap-2">
              <Plug className="w-3.5 h-3.5" />
              Connections
            </h3>
            <div className="flex gap-3">
              {agent.connections.map((conn) => (
                <div
                  key={conn.name}
                  className="flex items-center gap-2.5 px-4 py-2.5 rounded-xl bg-white/[0.03] border border-white/[0.06]"
                >
                  <div className="w-6 h-6 rounded bg-white/[0.08] flex items-center justify-center text-[10px] font-bold text-zinc-400">
                    {conn.name.charAt(0)}
                  </div>
                  <span className="text-[13px] text-zinc-300 font-medium">{conn.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action button */}
        <div className="p-8 pt-8">
          <button
            onClick={() => onHire?.(agent.id)}
            disabled={isHired}
            className={cn(
              'w-full py-3 rounded-xl text-[15px] font-semibold transition-colors',
              isHired
                ? 'bg-white/[0.06] text-zinc-500 cursor-default'
                : 'bg-white text-black hover:bg-zinc-200'
            )}
          >
            {isHired ? 'Already on Team' : 'Hire to Team'}
          </button>
          <p className="text-center text-[12px] text-zinc-600 mt-2">
            {isHired ? 'This agent is already on your team.' : 'Adds this agent to your team — assign them to cases anytime.'}
          </p>
        </div>
      </div>
    </div>
  )
}
