import { Routes, Route } from 'react-router-dom'

import { AppShell } from '@/components/layout/AppShell'
import { Calendar } from '@/pages/Calendar'
import { LoginPlaceholder } from '@/pages/LoginPlaceholder'
import { Manager } from '@/pages/Manager'
import { PlaceholderPage } from '@/pages/PlaceholderPage'
import { ServiceChat } from '@/pages/ServiceChat'
import { Marketplace } from '@/pages/Marketplace'
import { MarketplaceTwinPlaceholder } from '@/pages/MarketplaceTwinPlaceholder'
import { Services } from '@/pages/Services'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPlaceholder />} />
      <Route
        path="/*"
        element={
          <AppShell>
            <Routes>
              <Route path="/" element={<PlaceholderPage title="Overview" />} />
              <Route path="/manager" element={<Manager />} />
              <Route path="/services" element={<Services />} />
              <Route path="/services/:serviceId" element={<ServiceChat />} />
              <Route path="/marketplace" element={<Marketplace />} />
              <Route path="/marketplace/:twinId" element={<MarketplaceTwinPlaceholder />} />
              <Route path="/calendar" element={<Calendar />} />
            </Routes>
          </AppShell>
        }
      />
    </Routes>
  )
}
