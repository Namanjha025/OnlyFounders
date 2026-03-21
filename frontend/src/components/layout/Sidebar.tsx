import { useLocation, Link, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  Layers,
  Store,
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  Zap,
  Sparkles,
  LogOut,
} from 'lucide-react'
import { useState } from 'react'
import { cn, getInitials } from '@/lib/utils'
import { useAuth } from '@/lib/auth'

/** Static footer identity until auth is wired to OnlyFounders API */
const SIDEBAR_USER_NAME = 'Naman Jha'
const SIDEBAR_USER_ROLE = 'Founder'

const navItems = [
  { label: 'Overview', icon: LayoutDashboard, path: '/' },
  { label: 'Manager', icon: Sparkles, path: '/manager' },
  { label: 'Services', icon: Layers, path: '/services' },
  { label: 'Marketplace', icon: Store, path: '/marketplace' },
  { label: 'Calendar', icon: CalendarDays, path: '/calendar' },
]

export function Sidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const { logout } = useAuth()
  const [collapsed, setCollapsed] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside
      className={cn(
        'flex flex-col h-full border-r border-border bg-sidebar transition-all duration-300 relative',
        collapsed ? 'w-[68px]' : 'w-[260px]'
      )}
    >
      <div className={cn('flex items-center gap-3 px-5 h-16 border-b border-border', collapsed && 'justify-center px-0')}>
        <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-white text-black">
          <Zap className="w-4 h-4" strokeWidth={2.5} />
        </div>
        {!collapsed && (
          <div className="flex flex-col">
            <span className="text-base font-semibold text-foreground tracking-tight">OnlyFounders</span>
            <span className="text-xs text-muted-foreground font-medium tracking-wide uppercase">
              Startup workspace
            </span>
          </div>
        )}
      </div>

      <nav className="flex-1 py-4 px-3 space-y-1">
        {navItems.map((item) => {
          const isActive = item.path === '/'
            ? location.pathname === '/'
            : location.pathname.startsWith(item.path)

          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-[15px] font-medium transition-all duration-150 group relative',
                isActive
                  ? 'bg-white/[0.08] text-white'
                  : 'text-sidebar-foreground hover:bg-white/[0.04] hover:text-foreground'
              )}
            >
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-white rounded-r-full" />
              )}
              <item.icon className={cn('w-[18px] h-[18px] shrink-0', isActive ? 'text-white' : 'text-muted-foreground group-hover:text-foreground')} />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          )
        })}
      </nav>

      <div className="border-t border-border p-3">
        {!collapsed && (
          <div className="flex items-center gap-3 px-3 py-2 mb-2">
            <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-sm font-bold text-white">
              {getInitials(SIDEBAR_USER_NAME)}
            </div>
            <div className="flex-1 flex flex-col min-w-0">
              <span className="text-sm font-medium text-foreground truncate">{SIDEBAR_USER_NAME}</span>
              <span className="text-xs text-muted-foreground capitalize">{SIDEBAR_USER_ROLE}</span>
            </div>
            <button
              onClick={handleLogout}
              className="p-1.5 text-zinc-600 hover:text-zinc-300 transition-colors rounded-lg hover:bg-white/[0.06]"
              title="Sign out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex items-center justify-center w-full py-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-white/[0.04] transition-colors"
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>
    </aside>
  )
}
