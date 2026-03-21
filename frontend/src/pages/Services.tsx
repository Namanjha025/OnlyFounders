import { Link } from 'react-router-dom'
import { ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils'
import { SERVICE_CONFIG, SERVICE_IDS, type ServiceId } from '@/data/serviceAssistants'

export function Services() {
  return (
    <div className="animate-fade-in -m-8 min-h-screen flex flex-col bg-[#050507]">
      <div className="flex-1 flex flex-col px-6 pt-14 pb-10 sm:pt-10">
        <div className="max-w-3xl mx-auto w-full">
          <h1 className="text-2xl font-semibold text-foreground tracking-tight">Services</h1>
          <p className="text-[15px] text-muted-foreground mt-1">
            Pick a service to open its assistant — same full-page chat style as AI Manager.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 sm:gap-8 mt-16 sm:mt-20">
            {SERVICE_IDS.map((id: ServiceId) => {
              const s = SERVICE_CONFIG[id]
              const Icon = s.icon
              return (
                <Link
                  key={id}
                  to={`/services/${id}`}
                  className={cn(
                    'group text-left rounded-xl border border-white/[0.06] bg-white/[0.02] px-4 py-3.5 transition-all',
                    'hover:bg-white/[0.05] hover:border-white/[0.12] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring'
                  )}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex items-center justify-center w-10 h-10 rounded-lg shrink-0 bg-white/[0.06] group-hover:bg-white/[0.1] transition-colors">
                      <Icon className="w-5 h-5 text-zinc-400 group-hover:text-white transition-colors" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-[15px] font-medium text-foreground leading-snug pr-2">{s.title}</p>
                      <p className="text-xs text-muted-foreground mt-1 leading-relaxed">{s.description}</p>
                    </div>
                    <ChevronRight className="w-5 h-5 text-zinc-600 shrink-0 mt-2 group-hover:text-zinc-300 transition-colors" />
                  </div>
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
