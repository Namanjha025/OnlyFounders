import { useLocation, Link, useNavigate } from 'react-router-dom'
import {
  Sparkles,
  Activity,
  Bot,
  Store,
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  Zap,
  LogOut,
  Plus,
  User,
  Folder,
} from 'lucide-react'
import { useState, useEffect } from 'react'
import { cn, getInitials } from '@/lib/utils'
import { useAuth } from '@/lib/auth'
import { workspaces as wsApi, type WorkspaceSummary } from '@/lib/api'
import { resolveIcon } from '@/lib/icons'

export function Sidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const { logout, user, profile } = useAuth()
  const [collapsed, setCollapsed] = useState(false)
  const [workspacesOpen, setWorkspacesOpen] = useState(true)
  const [exploreOpen, setExploreOpen] = useState(true)
  const [wsList, setWsList] = useState<WorkspaceSummary[]>([])

  const userName = user ? `${user.first_name} ${user.last_name}` : 'User'
  const userRole = profile?.profile_type || user?.marketplace_role || 'Member'

  useEffect(() => {
    wsApi.list().then(setWsList).catch(() => {})
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const isActive = (path: string) => {
    if (path === '/') return location.pathname === '/'
    return location.pathname === path || location.pathname.startsWith(path + '/')
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

      <nav className="flex-1 py-4 px-3 space-y-0.5 overflow-y-auto">
        <NavItem to="/feed" icon={Activity} label="Feed" active={isActive('/feed')} collapsed={collapsed} />
        <NavItem to="/manager" icon={Sparkles} label="Chat" active={isActive('/manager')} collapsed={collapsed} />

        {!collapsed && (
          <div className="pt-5 pb-1">
            <button
              onClick={() => setWorkspacesOpen(!workspacesOpen)}
              className="flex items-center justify-between w-full px-3 group"
            >
              <span className="text-[11px] uppercase tracking-wider text-zinc-500 font-medium group-hover:text-zinc-400 transition-colors">
                My Workspaces
              </span>
              <div className="flex items-center gap-1">
                <Plus className="w-3.5 h-3.5 text-zinc-600 hover:text-zinc-300 transition-colors" />
                <ChevronDown className={cn('w-3.5 h-3.5 text-zinc-600 transition-transform', !workspacesOpen && '-rotate-90')} />
              </div>
            </button>
          </div>
        )}

        {(collapsed || workspacesOpen) && wsList.map((ws) => {
          const WsIcon = resolveIcon(ws.icon)
          const wsActive = location.pathname === `/workspaces/${ws.id}`
          return (
            <Link
              key={ws.id}
              to={`/workspaces/${ws.id}`}
              className={cn(
                'flex items-center gap-3 rounded-lg text-[14px] font-medium transition-all duration-150 group relative',
                collapsed ? 'px-3 py-2.5 justify-center' : 'px-3 py-2',
                wsActive ? 'bg-white/[0.08] text-white' : 'text-sidebar-foreground hover:bg-white/[0.04] hover:text-foreground'
              )}
            >
              {wsActive && !collapsed && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-white rounded-r-full" />
              )}
              <WsIcon className={cn('w-[16px] h-[16px] shrink-0', wsActive ? 'text-white' : 'text-muted-foreground group-hover:text-foreground')} />
              {!collapsed && <span className="truncate">{ws.name}</span>}
              {!collapsed && ws.notification_count > 0 && (
                <span className="ml-auto text-[11px] px-1.5 py-0.5 rounded-full bg-red-500/20 text-red-400 font-medium">
                  {ws.notification_count}
                </span>
              )}
            </Link>
          )
        })}

        {!collapsed && (
          <div className="pt-5 pb-1">
            <button
              onClick={() => setExploreOpen(!exploreOpen)}
              className="flex items-center justify-between w-full px-3 group"
            >
              <span className="text-[11px] uppercase tracking-wider text-zinc-500 font-medium group-hover:text-zinc-400 transition-colors">
                Explore
              </span>
              <ChevronDown className={cn('w-3.5 h-3.5 text-zinc-600 transition-transform', !exploreOpen && '-rotate-90')} />
            </button>
          </div>
        )}

        {(collapsed || exploreOpen) && (
          <>
            <NavItem to="/agents" icon={Bot} label="Agents" active={isActive('/agents')} collapsed={collapsed} />
            <NavItem to="/marketplace" icon={Store} label="Marketplace" active={isActive('/marketplace')} collapsed={collapsed} />
          </>
        )}

        {!collapsed && <div className="pt-3" />}
        <NavItem to="/calendar" icon={CalendarDays} label="Calendar" active={isActive('/calendar')} collapsed={collapsed} />
        <NavItem to="/marketplace/me" icon={User} label="My Profile" active={isActive('/marketplace/me')} collapsed={collapsed} indent />
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
            <button onClick={handleLogout} className="p-1.5 text-zinc-600 hover:text-zinc-300 transition-colors rounded-lg hover:bg-white/[0.06]" title="Sign out">
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

function NavItem({ to, icon: Icon, label, active, collapsed, badge, indent }: {
  to: string; icon: typeof Sparkles; label: string; active: boolean; collapsed: boolean; badge?: number; indent?: boolean
}) {
  return (
    <Link
      to={to}
      className={cn(
        'flex items-center gap-3 rounded-lg font-medium transition-all duration-150 group relative',
        indent ? 'text-[13px] px-3 py-1.5 pl-9' : 'text-[14px] px-3 py-2.5',
        collapsed && 'justify-center',
        active ? 'bg-white/[0.08] text-white' : 'text-sidebar-foreground hover:bg-white/[0.04] hover:text-foreground'
      )}
    >
      {active && !collapsed && !indent && (
        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-white rounded-r-full" />
      )}
      <Icon className={cn(indent ? 'w-[14px] h-[14px]' : 'w-[18px] h-[18px]', 'shrink-0', active ? 'text-white' : 'text-muted-foreground group-hover:text-foreground')} />
      {!collapsed && <span>{label}</span>}
      {!collapsed && badge != null && badge > 0 && (
        <span className="ml-auto text-[11px] px-1.5 py-0.5 rounded-full bg-red-500/20 text-red-400 font-medium">{badge}</span>
      )}
    </Link>
  )
}
