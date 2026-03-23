import { Routes, Route, Navigate } from 'react-router-dom'

import { useAuth } from '@/lib/auth'
import { AppShell } from '@/components/layout/AppShell'
import { Calendar } from '@/pages/Calendar'
import { LoginPlaceholder } from '@/pages/LoginPlaceholder'
import { Manager } from '@/pages/Manager'
import { Marketplace } from '@/pages/Marketplace'
import { MarketplaceTwinPlaceholder } from '@/pages/MarketplaceTwinPlaceholder'
import { MarketplaceProfilePage } from '@/pages/MarketplaceProfile'
import { MarketplaceDocuments } from '@/pages/MarketplaceDocuments'
import { Workspace } from '@/pages/Workspace'
import { Agents } from '@/pages/Agents'
import { InboxPage } from '@/pages/InboxPage'
import { Feed } from '@/pages/Feed'
import { Team } from '@/pages/Team'
import { Cases } from '@/pages/Cases'

export default function App() {
  const { user, hasProfile, loading } = useAuth()

  return (
    <Routes>
      <Route path="/login" element={<LoginPlaceholder />} />
      <Route
        path="/*"
        element={
          loading ? null :
          !user ? <Navigate to="/login" replace /> :
          !hasProfile ? <Navigate to="/login" replace /> :
          <AppShell>
            <Routes>
              <Route path="/" element={<Navigate to="/feed" replace />} />
              <Route path="/feed" element={<Feed />} />
              <Route path="/manager" element={<Manager />} />
              <Route path="/notifications" element={<InboxPage />} />
              <Route path="/team" element={<Team />} />
              <Route path="/cases" element={<Cases />} />
              <Route path="/cases/:workspaceId/*" element={<Workspace />} />
              <Route path="/agents" element={<Agents />} />
              <Route path="/marketplace" element={<Marketplace />} />
              <Route path="/marketplace/me" element={<MarketplaceProfilePage />} />
              <Route path="/marketplace/documents" element={<MarketplaceDocuments />} />
              <Route path="/marketplace/:twinId" element={<MarketplaceTwinPlaceholder />} />
              <Route path="/calendar" element={<Calendar />} />
            </Routes>
          </AppShell>
        }
      />
    </Routes>
  )
}
