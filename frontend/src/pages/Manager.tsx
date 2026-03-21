import { useState, useRef, useEffect } from 'react'
import { Paperclip, Sparkles, ArrowUp } from 'lucide-react'
import { cn } from '@/lib/utils'

/** Matches sidebar static user for greeting initials (NJ). */
const FOUNDER_FIRST_NAME = 'Naman'

interface Message {
  id: number
  role: 'assistant' | 'user'
  content: string
  time: string
}

const suggestions = [
  'What should I prioritize for my startup this week?',
  'Summarize my workspace: tasks, runway, and milestones',
  'What blockers or risks should I watch on my roadmap?',
  'How should I prepare for my next investor conversation?',
]

const initialMessages: Message[] = [
  {
    id: 1,
    role: 'assistant',
    content: `Good morning, ${FOUNDER_FIRST_NAME}. Here's a quick pulse on your **OnlyFounders workspace**:\n\n**Your startup** is set up with an active profile. **8 open tasks** span product, fundraising prep, and ops — 3 are due this week, including updating your traction metrics and refreshing the pitch deck appendix.\n\n**Documents:** your incorporation pack and last month's cap table snapshot are in the workspace; the data room still needs your latest **financial model** version.\n\n**Calendar:** you have a **founder sync** Thursday and a **demo dry-run** Friday.\n\nWhen the API is connected, I'll pull live data from your startup, tasks, docs, funding rounds, and calendar. For now, what do you want to tackle first?`,
    time: now(),
  },
]

function now() {
  return new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
}

export function Manager() {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, isTyping])

  const handleSend = (text?: string) => {
    const msg = text || input.trim()
    if (!msg) return

    const userMsg: Message = { id: Date.now(), role: 'user', content: msg, time: now() }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setIsTyping(true)

    setTimeout(() => {
      const reply = getReply(msg)
      setMessages((prev) => [...prev, { id: Date.now() + 1, role: 'assistant', content: reply, time: now() }])
      setIsTyping(false)
    }, 1200 + Math.random() * 800)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const showSuggestions = messages.length <= 1

  return (
    <div className="animate-fade-in -m-8 h-screen flex flex-col bg-[#050507]">
      <div className="flex-1 flex flex-col overflow-hidden">
        <div ref={scrollRef} className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-6 py-8 space-y-6">
            {messages.length <= 1 && (
              <div className="text-center pt-8 pb-4">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-white/[0.08] mb-4">
                  <Sparkles className="w-6 h-6 text-zinc-300" />
                </div>
                <h1 className="text-2xl font-semibold text-foreground tracking-tight">AI Manager</h1>
                <p className="text-[15px] text-muted-foreground mt-1 max-w-md mx-auto">
                  Your workspace copilot — startup context, tasks, documents, funding, and team (when your
                  backend is connected).
                </p>
              </div>
            )}

            {messages.map((msg) => (
              <div key={msg.id} className={cn('flex gap-3', msg.role === 'user' && 'flex-row-reverse')}>
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-lg bg-white/[0.08] flex items-center justify-center shrink-0 mt-1">
                    <Sparkles className="w-4 h-4 text-zinc-400" />
                  </div>
                )}
                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-white/[0.06] flex items-center justify-center text-[13px] font-bold text-zinc-400 shrink-0 mt-1">
                    NJ
                  </div>
                )}
                <div className={cn(msg.role === 'user' ? 'max-w-[70%] text-right' : 'max-w-[85%]')}>
                  <div
                    className={cn(
                      'rounded-2xl px-5 py-3.5 text-[15px] leading-relaxed whitespace-pre-line',
                      msg.role === 'assistant'
                        ? 'bg-white/[0.03] border border-white/[0.06] text-foreground'
                        : 'bg-white/[0.08] text-foreground'
                    )}
                  >
                    {formatMessage(msg.content)}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1.5 px-1">{msg.time}</p>
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-lg bg-white/[0.08] flex items-center justify-center shrink-0">
                  <Sparkles className="w-4 h-4 text-zinc-400" />
                </div>
                <div className="bg-white/[0.03] border border-white/[0.06] rounded-2xl px-5 py-3.5">
                  <div className="flex gap-1.5">
                    <div className="w-2 h-2 bg-zinc-500 rounded-full animate-pulse" />
                    <div className="w-2 h-2 bg-zinc-500 rounded-full animate-pulse [animation-delay:150ms]" />
                    <div className="w-2 h-2 bg-zinc-500 rounded-full animate-pulse [animation-delay:300ms]" />
                  </div>
                </div>
              </div>
            )}

            {showSuggestions && (
              <div className="grid grid-cols-2 gap-2 pt-2">
                {suggestions.map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => handleSend(s)}
                    className="text-left p-3.5 rounded-xl border border-white/[0.06] bg-white/[0.02] hover:bg-white/[0.05] hover:border-white/[0.12] transition-all text-[14px] text-zinc-400 hover:text-foreground"
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="shrink-0 pb-6 pt-2 px-6">
          <div className="max-w-3xl mx-auto">
            <div className="flex items-center gap-2 bg-card border border-white/[0.08] rounded-xl px-4 py-3.5">
              <input
                type="text"
                placeholder="Ask your AI Manager about your startup workspace..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                className="flex-1 bg-transparent text-[15px] text-foreground placeholder:text-muted-foreground focus:outline-none"
              />
              <button type="button" className="p-1.5 text-muted-foreground hover:text-foreground transition-colors">
                <Paperclip className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => handleSend()}
                disabled={!input.trim()}
                className={cn(
                  'p-2 rounded-lg transition-colors',
                  input.trim() ? 'bg-white text-black hover:bg-zinc-200' : 'bg-zinc-800 text-zinc-400 cursor-not-allowed'
                )}
              >
                <ArrowUp className="w-4 h-4" />
              </button>
            </div>
            <p className="text-center text-xs text-zinc-400 mt-2">
              With the API connected, Manager reads your startup profile, tasks, documents, funding, and calendar —
              per OnlyFounders specs.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

function formatMessage(content: string) {
  const parts = content.split(/(\*\*[^*]+\*\*)/g)
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return (
        <strong key={i} className="font-semibold text-white">
          {part.slice(2, -2)}
        </strong>
      )
    }
    return part
  })
}

function getReply(msg: string): string {
  const lower = msg.toLowerCase()
  if (lower.includes('priorit') || lower.includes('this week') || lower.includes('focus')) {
    return `Here's a sensible **priority stack** for your startup this week:\n\n**1. Close the loop on metrics** — Update traction numbers in the workspace so the Manager (and future investors) see a current picture.\n\n**2. Unblock fundraising prep** — Finish the financial model upload and reconcile runway assumptions with your cap table.\n\n**3. Ship one visible product increment** — Protect a deep-work block for the highest-impact task on your board.\n\n**4. Team & ops** — Confirm who's owning investor outreach and legal follow-ups so nothing slips.\n\nWant this tailored once your real task due dates are synced from the API?`
  }
  if (lower.includes('summar') || lower.includes('workspace') || lower.includes('status') || lower.includes('milestone')) {
    return `**Workspace snapshot** (illustrative until live data loads):\n\n**Startup** — Profile active; stage and industry set in OnlyFounders.\n\n**Tasks** — 8 open: 3 due this week (traction update, deck appendix, investor CRM cleanup).\n\n**Runway** — Financial details in the app will drive this; plug in burn and cash to see weeks-of-runway here.\n\n**Milestones** — Demo dry-run Friday; founder sync Thursday; target: seed materials “investor-ready” by month-end.\n\nConnect the backend to replace this with your real tasks, documents, funding rounds, and calendar events.`
  }
  if (lower.includes('risk') || lower.includes('blocker') || lower.includes('roadmap') || lower.includes('watch')) {
    return `**Risks & blockers** to keep on your radar:\n\n**Runway / fundraising** — If the model isn't updated, you may misestimate months of cash left ahead of investor conversations.\n\n**Single-threaded work** — Too many parallel initiatives slows shipping; watch for tasks stuck in "in progress" with no owner.\n\n**Document drift** — Pitch deck, data room, and cap table should version together before you send materials out.\n\n**Compliance & cap table** — ESOP promises or SAFEs that aren't reflected in the workspace create surprises later.\n\nTell me your stage (pre-seed / seed / Series A) and I can stress-test a tighter list.`
  }
  if (lower.includes('investor') || lower.includes('funding') || lower.includes('pitch') || lower.includes('conversation')) {
    return `**Next investor conversation** — prep checklist:\n\n**Narrative** — 5-minute story: problem, why now, traction, why you, use of funds.\n\n**Numbers** — MRR/ARR or leading indicator, burn, runway, and a clear ask (amount, structure, timeline).\n\n**Materials** — One-pager, deck, data room index; make sure the cap table matches what you'll say live.\n\n**Due diligence** — Incorporation, IP assignments, major contracts, and any prior SAFEs or notes ready to share.\n\n**Follow-up** — Decide what you'll send within 24 hours and who owns it.\n\nWhen OnlyFounders exposes funding rounds and financials via API, I can align this with your actual raise status.`
  }
  if (lower.includes('document') || lower.includes('upload') || lower.includes('deck') || lower.includes('data room')) {
    return `**Documents** worth having in your OnlyFounders workspace:\n\n- **Pitch deck** (latest PDF)\n- **Incorporation** & board resolutions\n- **Cap table** / equity ledger\n- **Financial model** and historical P&L if you have it\n- **Key contracts** (customers, pilots, advisors)\n\nThe document module is S3-backed in the backend — once wired to the UI, I'll be able to reference what's uploaded and what's missing. Want a minimal vs investor-grade doc list?`
  }
  return `I'm here to help with **your startup workspace** on OnlyFounders — priorities, tasks, documents, funding prep, team context, and roadmap risks.\n\nYou said: "${msg.slice(0, 50)}${msg.length > 50 ? '...' : ''}"\n\nBe more specific (e.g. runway, hiring, product milestone, or investor meeting), or connect the API so I can use your real workspace data from startups, tasks, documents, and calendar — as described in the Manager specs.`
}
