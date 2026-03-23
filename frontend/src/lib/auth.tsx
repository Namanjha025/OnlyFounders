import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { api, marketplace, type UserResponse, type MarketplaceProfile } from './api'

interface AuthState {
  user: UserResponse | null
  profile: MarketplaceProfile | null
  loading: boolean
  hasProfile: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: { email: string; password: string; first_name: string; last_name: string }) => Promise<void>
  logout: () => void
  refreshProfile: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null)
  const [profile, setProfile] = useState<MarketplaceProfile | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchProfile = async () => {
    try {
      const p = await marketplace.getMyProfile()
      setProfile(p)
    } catch {
      setProfile(null)
    }
  }

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      Promise.all([
        api.me().then(setUser).catch(() => localStorage.removeItem('token')),
        fetchProfile(),
      ]).finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    const res = await api.login({ email, password })
    localStorage.setItem('token', res.access_token)
    const u = await api.me()
    setUser(u)
    await fetchProfile()
  }

  const register = async (data: { email: string; password: string; first_name: string; last_name: string }) => {
    const res = await api.register(data)
    localStorage.setItem('token', res.access_token)
    setUser(res.user)
    // No profile yet after register — will go through onboarding
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
    setProfile(null)
  }

  const refreshProfile = async () => {
    await fetchProfile()
  }

  return (
    <AuthContext.Provider value={{ user, profile, loading, hasProfile: profile !== null, login, register, logout, refreshProfile }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
