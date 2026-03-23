import { Routes, Route, Navigate } from 'react-router-dom'

import { useAuth } from '@/lib/auth'
import { AppShell } from '@/components/layout/AppShell'
import { Calendar } from '@/pages/Calendar'
import { LoginPlaceholder } from '@/pages/LoginPlaceholder'
import { Manager } from '@/pages/Manager'
import { PlaceholderPage } from '@/pages/PlaceholderPage'
import { ServiceChat } from '@/pages/ServiceChat'
import { Marketplace } from '@/pages/Marketplace'
import { MarketplaceTwinPlaceholder } from '@/pages/MarketplaceTwinPlaceholder'
import { MarketplaceProfilePage } from '@/pages/MarketplaceProfile'
import { MarketplaceDocuments } from '@/pages/MarketplaceDocuments'
import { Services } from '@/pages/Services'

function RequireProfile() {
  const { user, hasProfile, loading } = useAuth()
  if (loading) return null
  if (!user) return <Navigate to="/login" replace />
  if (!hasProfile) return <Navigate to="/login" replace />
  return null
}

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
              <Route path="/" element={<PlaceholderPage title="Overview" />} />
              <Route path="/manager" element={<Manager />} />
              <Route path="/services" element={<Services />} />
              <Route path="/services/:serviceId" element={<ServiceChat />} />
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
