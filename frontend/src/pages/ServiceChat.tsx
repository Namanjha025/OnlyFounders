import { useState, useRef, useEffect } from 'react'
import { Link, Navigate, useParams } from 'react-router-dom'
import { ArrowLeft, ArrowUp, Paperclip, Sparkles } from 'lucide-react'
import { cn } from '@/lib/utils'
import {
  SERVICE_CONFIG,
  getReply,
  isServiceId,
  type ServiceId,
} from '@/data/serviceAssistants'

interface Message {
  id: number
  role: 'assistant' | 'user'
  content: string
  time: string
}

function now() {
  return new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
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

function buildInitialMessages(serviceId: ServiceId): Message[] {
  return [
    {
      id: 1,
      role: 'assistant',
      content: SERVICE_CONFIG[serviceId].welcome,
      time: now(),
    },
  ]
}

export function ServiceChat() {
  const { serviceId: param } = useParams<{ serviceId: string }>()

  if (!param || !isServiceId(param)) {
    return <Navigate to="/services" replace />
  }

  const serviceId = param

  const [messages, setMessages] = useState<Message[]>(() => buildInitialMessages(serviceId))
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  const cfg = SERVICE_CONFIG[serviceId]

  useEffect(() => {
    setMessages(buildInitialMessages(serviceId))
    setInput('')
    setIsTyping(false)
  }, [serviceId])

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
      const reply = getReply(msg, serviceId)
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
      <div className="shrink-0 border-b border-white/[0.06] px-6 py-3">
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <Link
            to="/services"
            className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors rounded-lg px-2 py-1.5 -ml-2 hover:bg-white/[0.04]"
          >
            <ArrowLeft className="w-4 h-4" />
            Services
          </Link>
        </div>
      </div>

      <div className="flex-1 flex flex-col overflow-hidden min-h-0">
        <div ref={scrollRef} className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-6 py-8 space-y-6">
            {messages.length <= 1 && (
              <div className="text-center pt-4 pb-2">
                <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-white/[0.08] mb-4">
                  <Sparkles className="w-6 h-6 text-zinc-300" />
                </div>
                <h1 className="text-2xl font-semibold text-foreground tracking-tight">{cfg.title}</h1>
                <p className="text-[15px] text-muted-foreground mt-1">{cfg.description}</p>
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
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2">
                {cfg.suggestions.map((s) => (
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
                placeholder={`Ask about ${cfg.title.toLowerCase()}...`}
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
            <p className="text-center text-xs text-zinc-500 mt-2">
              Guidance only — verify schemes and MCA steps on official portals before you act.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
