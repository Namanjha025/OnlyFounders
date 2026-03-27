import { useEffect, useState, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { MapPin, Heart, Briefcase, Users, CheckCircle2, ArrowUp, MessageSquare } from 'lucide-react'
import { cn } from '@/lib/utils'
import { agents as agentsApi, team as teamApi, type AgentOut, type TeamAgentOut } from '@/lib/api'
import { resolveIcon } from '@/lib/icons'
import {
  avatarGradientVivid,
  ProfileTopBar, ProfileSection, ProfileSidebarCard, QuickInfoRow, ScoreRing,
} from '@/components/shared'

interface ChatMsg { id: number; role: 'user' | 'assistant'; content: string }

export function AgentProfile() {
  const { agentId } = useParams<{ agentId: string }>()
  const [agent, setAgent] = useState<AgentOut | null>(null)
  const [teamList, setTeamList] = useState<TeamAgentOut[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [chatOpen, setChatOpen] = useState(false)
  const [chatMsgs, setChatMsgs] = useState<ChatMsg[]>([])
  const [chatInput, setChatInput] = useState('')
  const [chatSending, setChatSending] = useState(false)
  const chatEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!agentId) return
    agentsApi.get(agentId)
      .then((a) => setAgent(a))
      .catch((err) => setError(err instanceof Error ? err.message : 'Not found'))
    teamApi.list()
      .then((t) => setTeamList(t))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [agentId])

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [chatMsgs])

  const handleChatSend = async () => {
    if (!chatInput.trim() || !agent?.endpoint_url || chatSending) return
    const text = chatInput.trim()
    setChatInput('')
    setChatMsgs((prev) => [...prev, { id: Date.now(), role: 'user', content: text }])
    setChatSending(true)
    try {
      const resp = await fetch(agent.endpoint_url + '/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          history: chatMsgs.map((m) => ({ role: m.role, content: m.content })),
        }),
      })
      const data = await resp.json()
      setChatMsgs((prev) => [...prev, { id: Date.now() + 1, role: 'assistant', content: data.message || '[No response]' }])
    } catch {
      setChatMsgs((prev) => [...prev, { id: Date.now() + 1, role: 'assistant', content: '[Failed to reach agent]' }])
    }
    setChatSending(false)
  }

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
        <a href="/agents" className="text-zinc-300 hover:underline text-sm">Back to agents</a>
      </div>
    </div>
  )
  if (!agent) return null

  const Icon = resolveIcon(agent.icon)
  const capabilities = agent.capabilities ?? []
  const instructions = agent.instructions ?? []
  const connections = agent.connections ?? []
  const capScore = Math.min(capabilities.length / 10, 1)
  const ringColor = capScore >= 0.8 ? '#22d3ee' : capScore >= 0.6 ? '#34d399' : capScore >= 0.4 ? '#facc15' : '#52525b'

  return (
    <div className="animate-fade-in -m-8 min-h-screen bg-background text-white">
      <ProfileTopBar
        backTo="/agents"
        backLabel="Back to agents"
        action={!isHired ? (
          <button
            onClick={handleHire}
            className="flex items-center gap-2 bg-white text-black px-4 py-1.5 rounded-lg text-sm font-semibold hover:bg-zinc-300 transition"
          >
            <Users className="w-3.5 h-3.5" /> Hire to Team
          </button>
        ) : undefined}
      />

      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-6">

          {/* ── Left Column ──────────────────────────────────────── */}
          <div className="space-y-6">
            {/* Avatar + Name — same pattern as marketplace */}
            <ProfileSection padding="p-8">
              <div className="flex flex-col items-center">
                <div className="w-28 h-28 rounded-full border-[3px] border-white/40 p-1">
                  <div
                    className="w-full h-full rounded-full flex items-center justify-center"
                    style={{ background: avatarGradientVivid(agent.name) }}
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
            </ProfileSection>

            {/* About + Capabilities — same as About + Skills in marketplace */}
            {(agent.description || capabilities.length > 0) && (
              <ProfileSection title="About">
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
              </ProfileSection>
            )}

            {/* Instructions — same pattern as "How I Can Help" */}
            {instructions.length > 0 && (
              <ProfileSection title="What This Agent Does" icon={Heart}>
                {instructions.map((instruction, i) => (
                  <div key={i} className="border-l-2 border-white/30 pl-4 mb-3 last:mb-0">
                    <p className="text-sm text-zinc-400">{instruction}</p>
                  </div>
                ))}
              </ProfileSection>
            )}

            {/* Connections — same pattern as Professional Details */}
            {connections.length > 0 && (
              <ProfileSection title="Connections & Integrations" icon={Briefcase}>
                <div className="grid grid-cols-2 gap-4">
                  {connections.map((conn) => (
                    <div key={conn.name}>
                      <p className="text-[11px] uppercase tracking-wider text-zinc-500 mb-1">Integration</p>
                      <p className="text-sm text-zinc-200">{conn.name}</p>
                    </div>
                  ))}
                </div>
              </ProfileSection>
            )}

            {/* Chat section */}
            {chatOpen && agent.endpoint_url && (
              <ProfileSection title="Chat" icon={MessageSquare}>
                <div className="flex flex-col h-[400px]">
                  <div className="flex-1 overflow-y-auto space-y-3 mb-3 pr-1">
                    {chatMsgs.length === 0 && (
                      <p className="text-xs text-zinc-500 text-center py-8">Send a message to start chatting with {agent.name}</p>
                    )}
                    {chatMsgs.map((m) => (
                      <div key={m.id} className={cn('flex', m.role === 'user' ? 'justify-end' : 'justify-start')}>
                        <div className={cn(
                          'max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed',
                          m.role === 'user'
                            ? 'bg-white/10 text-zinc-200'
                            : 'bg-white/[0.04] border border-white/[0.06] text-zinc-300'
                        )}>
                          <p className="whitespace-pre-wrap">{m.content}</p>
                        </div>
                      </div>
                    ))}
                    {chatSending && (
                      <div className="flex justify-start">
                        <div className="bg-white/[0.04] border border-white/[0.06] rounded-2xl px-4 py-3">
                          <div className="flex gap-1">
                            <span className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                            <span className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                            <span className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={chatEndRef} />
                  </div>
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleChatSend()}
                      placeholder={`Message ${agent.name}...`}
                      className="flex-1 bg-white/[0.06] border border-white/[0.08] rounded-xl px-4 py-2.5 text-sm text-zinc-200 placeholder:text-zinc-600 outline-none focus:border-white/20 transition"
                    />
                    <button
                      onClick={handleChatSend}
                      disabled={!chatInput.trim() || chatSending}
                      className="shrink-0 w-10 h-10 rounded-xl bg-white/10 hover:bg-white/20 disabled:opacity-30 flex items-center justify-center transition"
                    >
                      <ArrowUp className="w-4 h-4 text-zinc-200" />
                    </button>
                  </div>
                </div>
              </ProfileSection>
            )}
          </div>

          {/* ── Right Column ─────────────────────────────────────── */}
          <div className="space-y-4">
            {/* Hire card — same pattern as Connect card */}
            <ProfileSidebarCard title="Add to Team">
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
            </ProfileSidebarCard>

            {/* Chat button */}
            {agent.endpoint_url && (
              <ProfileSidebarCard title="Chat">
                <p className="text-xs text-zinc-500 mb-3">
                  Talk directly with this agent to learn more or start a task.
                </p>
                <button
                  onClick={() => setChatOpen((v) => !v)}
                  className={cn(
                    'w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-medium transition',
                    chatOpen
                      ? 'bg-white/10 text-white'
                      : 'border border-white/20 text-zinc-300 hover:bg-white/5 hover:border-white/30'
                  )}
                >
                  <MessageSquare className="w-4 h-4" /> {chatOpen ? 'Close Chat' : 'Chat with Agent'}
                </button>
              </ProfileSidebarCard>
            )}

            {/* Quick Info — same component as marketplace */}
            <ProfileSidebarCard title="Quick Info">
              <dl className="space-y-2.5">
                <QuickInfoRow label="Category"><span className="capitalize">{agent.category || 'General'}</span></QuickInfoRow>
                <QuickInfoRow label="Type"><span className="capitalize">{agent.agent_type}</span></QuickInfoRow>
                <QuickInfoRow label="Capabilities">{capabilities.length}</QuickInfoRow>
                <QuickInfoRow label="Connections">{connections.length}</QuickInfoRow>
              </dl>
            </ProfileSidebarCard>

            {/* Score ring — same component as marketplace */}
            <div className="rounded-2xl border border-border bg-card p-5 flex flex-col items-center">
              <ScoreRing
                value={capScore}
                label="skills"
                color={ringColor}
              />
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
