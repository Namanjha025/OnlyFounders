/** Dev: Vite proxy → backend :8000. Prod: set VITE_API_BASE_URL (e.g. https://api.example.com/api/v1). */
const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') || '/api/v1'

function getToken(): string | null {
  return localStorage.getItem('token')
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(body.detail || `HTTP ${res.status}`)
  }

  return res.json()
}

export const api = {
  register: (data: {
    email: string
    password: string
    first_name: string
    last_name: string
  }) => request<RegisterResponse>('/auth/register', { method: 'POST', body: JSON.stringify(data) }),

  login: (data: { email: string; password: string }) =>
    request<LoginResponse>('/auth/login', { method: 'POST', body: JSON.stringify(data) }),

  me: () => request<UserResponse>('/auth/me'),
}

export interface UserResponse {
  id: string
  email: string
  first_name: string
  last_name: string
  role: string
  is_active: boolean
  marketplace_role?: string | null
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface RegisterResponse {
  access_token: string
  token_type: string
  user: UserResponse
}

// ── Marketplace ─────────────────────────────────────────────────

export interface MarketplaceProfile {
  id: string
  user_id?: string
  profile_type: 'professional' | 'advisor' | 'founder'
  display_name?: string | null
  headline: string | null
  bio: string | null
  avatar_url: string | null
  location: string | null
  skills: string[]
  linkedin_url?: string | null
  website_url?: string | null
  profile_score: number
  is_public?: boolean
  visibility_settings?: Record<string, boolean>
  extra_data?: Record<string, unknown>
  profile_views?: number
  professional_data?: Record<string, unknown> | null
  advisor_data?: Record<string, unknown> | null
  founder_data?: Record<string, unknown> | null
  documents?: ProfileDocument[]
  primary_role?: string | null
  availability_status?: string | null
  created_at?: string
  updated_at?: string
}

export interface ProfileDocument {
  id: string
  document_type: string | null
  title: string
  s3_url: string
  file_size: number | null
  mime_type: string | null
  is_public: boolean
  sort_order: number
  created_at: string
}

export interface DiscoverResponse {
  items: MarketplaceProfile[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface OnboardingStatus {
  profile_id: string
  profile_type: string
  current_step: number
  total_steps: number
  completed_steps: number[]
  profile_score: number
  is_complete: boolean
}

export interface VisibilitySettings {
  is_public: boolean
  show_email: boolean
  show_phone: boolean
  show_linkedin: boolean
  show_location: boolean
  discoverable_in_search: boolean
}

export interface FacetBucket {
  value: string
  count: number
}

export interface FacetResponse {
  profile_types: FacetBucket[]
  skills: FacetBucket[]
  availability: FacetBucket[]
  hourly_rate_ranges: FacetBucket[]
  locations: FacetBucket[]
}

export interface PaginatedResponse extends DiscoverResponse {
  facets?: FacetResponse | null
}

function qs(params?: Record<string, string>): string {
  if (!params) return ''
  const filtered = Object.fromEntries(Object.entries(params).filter(([, v]) => v !== '' && v != null))
  return Object.keys(filtered).length ? '?' + new URLSearchParams(filtered).toString() : ''
}

export const marketplace = {
  // Discovery (Phase 2)
  discover: (params?: Record<string, string>) =>
    request<PaginatedResponse>(`/marketplace/discover${qs(params)}`),

  discoverProfessionals: (params?: Record<string, string>) =>
    request<PaginatedResponse>(`/marketplace/discover/professionals${qs(params)}`),

  discoverAdvisors: (params?: Record<string, string>) =>
    request<PaginatedResponse>(`/marketplace/discover/advisors${qs(params)}`),

  discoverFounders: (params?: Record<string, string>) =>
    request<PaginatedResponse>(`/marketplace/discover/founders${qs(params)}`),

  search: (params: Record<string, string>) =>
    request<PaginatedResponse>(`/marketplace/search${qs(params)}`),

  searchFacets: (params?: Record<string, string>) =>
    request<FacetResponse>(`/marketplace/search/facets${qs(params)}`),

  // Profile CRUD
  createProfile: (data: Record<string, unknown>) =>
    request<MarketplaceProfile>('/marketplace/profiles', { method: 'POST', body: JSON.stringify(data) }),

  getMyProfile: () =>
    request<MarketplaceProfile>('/marketplace/profiles/me'),

  getProfile: (id: string) =>
    request<MarketplaceProfile>(`/marketplace/profiles/${id}`),

  updateProfile: (data: Record<string, unknown>) =>
    request<MarketplaceProfile>('/marketplace/profiles/me', { method: 'PATCH', body: JSON.stringify(data) }),

  updateTypeData: (data: Record<string, unknown>) =>
    request<MarketplaceProfile>('/marketplace/profiles/me/type-data', { method: 'PATCH', body: JSON.stringify(data) }),

  deleteProfile: () =>
    request<void>('/marketplace/profiles/me', { method: 'DELETE' }),

  // Onboarding
  startOnboarding: (profile_type: string) =>
    request<OnboardingStatus>('/marketplace/onboarding/start', { method: 'POST', body: JSON.stringify({ profile_type }) }),

  saveStep: (step: number, data: Record<string, unknown>) =>
    request<OnboardingStatus>(`/marketplace/onboarding/step/${step}`, { method: 'PATCH', body: JSON.stringify({ data }) }),

  getOnboardingStatus: () =>
    request<OnboardingStatus>('/marketplace/onboarding/status'),

  // Visibility
  getVisibility: () =>
    request<VisibilitySettings>('/marketplace/profiles/me/visibility'),

  updateVisibility: (data: Partial<VisibilitySettings>) =>
    request<VisibilitySettings>('/marketplace/profiles/me/visibility', { method: 'PATCH', body: JSON.stringify(data) }),
}
