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
  User,
} from 'lucide-react'
import { useState } from 'react'
import { cn, getInitials } from '@/lib/utils'
import { useAuth } from '@/lib/auth'


const navItems = [
  { label: 'Overview', icon: LayoutDashboard, path: '/' },
  { label: 'Manager', icon: Sparkles, path: '/manager' },
  { label: 'Services', icon: Layers, path: '/services' },
  { label: 'Marketplace', icon: Store, path: '/marketplace' },
  { label: 'My Profile', icon: User, path: '/marketplace/me', indent: true },
  { label: 'Calendar', icon: CalendarDays, path: '/calendar' },
]

export function Sidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const { logout, user, profile } = useAuth()
  const [collapsed, setCollapsed] = useState(false)

  const userName = user ? `${user.first_name} ${user.last_name}` : 'User'
  const userRole = profile?.profile_type || user?.marketplace_role || 'Member'

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

      <nav className="flex-1 py-4 px-3 space-y-0.5">
        {navItems.map((item) => {
          const isActive = item.path === '/'
            ? location.pathname === '/'
            : item.path === '/marketplace'
            ? location.pathname === '/marketplace'
            : location.pathname.startsWith(item.path)

          const isIndented = 'indent' in item && item.indent

          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'flex items-center gap-3 rounded-lg text-[15px] font-medium transition-all duration-150 group relative',
                isIndented ? 'px-3 py-1.5 pl-9 text-[13px]' : 'px-3 py-2.5',
                isActive
                  ? 'bg-white/[0.08] text-white'
                  : 'text-sidebar-foreground hover:bg-white/[0.04] hover:text-foreground'
              )}
            >
              {isActive && !isIndented && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-white rounded-r-full" />
              )}
              <item.icon className={cn(isIndented ? 'w-[14px] h-[14px]' : 'w-[18px] h-[18px]', 'shrink-0', isActive ? 'text-white' : 'text-muted-foreground group-hover:text-foreground')} />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          )
        })}
      </nav>

      <div className="border-t border-border p-3">
        {!collapsed && (
          <div className="flex items-center gap-3 px-3 py-2 mb-2">
            <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-sm font-bold text-white">
              {getInitials(userName)}
            </div>
            <div className="flex-1 flex flex-col min-w-0">
              <span className="text-sm font-medium text-foreground truncate">{userName}</span>
              <span className="text-xs text-muted-foreground capitalize">{userRole}</span>
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
