import type { ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { NotificationBell } from './NotificationBell'

export function AppShell({ children }: { children: ReactNode }) {
  const location = useLocation()
  const isFullPage = location.pathname.match(/^\/cases\/[^/]+/)

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        {!isFullPage && (
          <div className="shrink-0 h-12 flex items-center justify-end px-5 border-b border-white/[0.04]">
            <NotificationBell />
          </div>
        )}
        <main className={isFullPage ? 'flex-1 flex flex-col min-h-0' : 'flex-1 overflow-y-auto'}>
          <div className={isFullPage ? 'flex-1 flex flex-col min-h-0' : 'p-8'}>
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
