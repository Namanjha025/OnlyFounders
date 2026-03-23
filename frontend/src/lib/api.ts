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

// ── Workspaces ──────────────────────────────────────────────────

export type CaseStatus = 'open' | 'in_progress' | 'resolved'

export interface WorkspaceSummary {
  id: string
  name: string
  workspace_type: 'ongoing' | 'goal'
  case_status: CaseStatus
  icon: string | null
  status_text: string | null
  progress: number | null
  agent_count: number
  task_done_count: number
  task_total_count: number
  notification_count: number
  created_at: string
}

export interface WorkspaceAgentOut {
  id: string
  agent_id: string
  agent_name: string | null
  agent_slug: string | null
  agent_description: string | null
  agent_category: string | null
  agent_icon: string | null
  agent_color: string | null
  created_at: string
}

export interface WorkspaceTaskOut {
  id: string
  workspace_id: string
  agent_id: string | null
  title: string
  description: string | null
  assignee_name: string | null
  is_done: boolean
  created_at: string
  updated_at: string
}

export interface WorkspaceMessageOut {
  id: string
  workspace_id: string
  agent_id: string | null
  user_id: string | null
  role: 'user' | 'assistant' | 'activity'
  content: string
  action_buttons: Record<string, unknown> | null
  agent_name: string | null
  agent_icon: string | null
  agent_color: string | null
  created_at: string
}

export interface WorkspaceOut {
  id: string
  user_id: string
  name: string
  workspace_type: 'ongoing' | 'goal'
  case_status: CaseStatus
  goal: string | null
  brief: string | null
  status_text: string | null
  progress: number | null
  icon: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  agents: WorkspaceAgentOut[]
  tasks: WorkspaceTaskOut[]
  notification_count: number
}

export const workspaces = {
  list: () =>
    request<WorkspaceSummary[]>('/workspaces/'),

  get: (id: string) =>
    request<WorkspaceOut>(`/workspaces/${id}`),

  create: (data: { name: string; workspace_type?: string; case_status?: CaseStatus; goal?: string; icon?: string }) =>
    request<WorkspaceOut>('/workspaces/', { method: 'POST', body: JSON.stringify(data) }),

  update: (id: string, data: Record<string, unknown>) =>
    request<WorkspaceOut>(`/workspaces/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  addAgent: (workspaceId: string, agentId: string) =>
    request<WorkspaceAgentOut>(`/workspaces/${workspaceId}/agents/${agentId}`, { method: 'POST' }),

  removeAgent: (workspaceId: string, agentId: string) =>
    request<void>(`/workspaces/${workspaceId}/agents/${agentId}`, { method: 'DELETE' }),

  listMessages: (id: string, limit = 50, offset = 0) =>
    request<WorkspaceMessageOut[]>(`/workspaces/${id}/messages?limit=${limit}&offset=${offset}`),

  sendMessage: (id: string, content: string) =>
    request<WorkspaceMessageOut>(`/workspaces/${id}/messages`, { method: 'POST', body: JSON.stringify({ content }) }),

  listTasks: (id: string) =>
    request<WorkspaceTaskOut[]>(`/workspaces/${id}/tasks`),

  createTask: (id: string, data: { title: string; description?: string; agent_id?: string }) =>
    request<WorkspaceTaskOut>(`/workspaces/${id}/tasks`, { method: 'POST', body: JSON.stringify(data) }),

  updateTask: (workspaceId: string, taskId: string, data: Record<string, unknown>) =>
    request<WorkspaceTaskOut>(`/workspaces/${workspaceId}/tasks/${taskId}`, { method: 'PUT', body: JSON.stringify(data) }),
}

// ── Notifications ───────────────────────────────────────────────

export interface NotificationOut {
  id: string
  user_id: string
  workspace_id: string | null
  agent_id: string | null
  notification_type: 'approval' | 'report'
  priority: 'high' | 'medium' | 'low'
  title: string
  description: string | null
  detail: string | null
  is_read: boolean
  action_buttons: Record<string, unknown> | null
  agent_name: string | null
  agent_icon: string | null
  agent_color: string | null
  workspace_name: string | null
  created_at: string
}

export const notifications = {
  list: (params?: { type?: string; unread_only?: boolean; limit?: number; offset?: number }) => {
    const q = new URLSearchParams()
    if (params?.type) q.set('type', params.type)
    if (params?.unread_only) q.set('unread_only', 'true')
    if (params?.limit) q.set('limit', String(params.limit))
    if (params?.offset) q.set('offset', String(params.offset))
    const qs = q.toString()
    return request<NotificationOut[]>(`/notifications/${qs ? '?' + qs : ''}`)
  },

  unreadCount: () =>
    request<{ unread_count: number }>('/notifications/count'),

  markRead: (id: string) =>
    request<NotificationOut>(`/notifications/${id}/read`, { method: 'PUT' }),

  markAllRead: () =>
    request<void>('/notifications/read-all', { method: 'PUT' }),
}

// ── Feed ────────────────────────────────────────────────────────

export interface FeedEventOut {
  id: string
  user_id: string
  workspace_id: string
  agent_id: string | null
  event_type: 'task_complete' | 'task_started' | 'file_created' | 'status_update' | 'approval_request'
  title: string
  description: string | null
  agent_name: string | null
  agent_icon: string | null
  agent_color: string | null
  workspace_name: string | null
  created_at: string
}

export const feed = {
  list: (limit = 50, offset = 0) =>
    request<FeedEventOut[]>(`/feed/?limit=${limit}&offset=${offset}`),
}

// ── Agents (catalog) ────────────────────────────────────────────

export interface AgentOut {
  id: string
  name: string
  slug: string
  description: string | null
  agent_type: string
  category: string | null
  icon: string | null
  color: string | null
  capabilities: string[] | null
  instructions: string[] | null
  connections: { name: string; icon?: string }[] | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export const agents = {
  list: () =>
    request<AgentOut[]>('/agents/'),

  get: (id: string) =>
    request<AgentOut>(`/agents/${id}`),
}

// ── Team ────────────────────────────────────────────────────────

export interface TeamAgentOut {
  id: string
  user_id: string
  agent_id: string
  role: string | null
  job_description: string | null
  agent_name: string | null
  agent_slug: string | null
  agent_description: string | null
  agent_category: string | null
  agent_icon: string | null
  agent_color: string | null
  agent_capabilities: string[] | null
  created_at: string
  updated_at: string
}

export const team = {
  list: () =>
    request<TeamAgentOut[]>('/team/'),

  hire: (data: { agent_id: string; role?: string; job_description?: string }) =>
    request<TeamAgentOut>('/team/', { method: 'POST', body: JSON.stringify(data) }),

  update: (id: string, data: { role?: string; job_description?: string }) =>
    request<TeamAgentOut>(`/team/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  remove: (id: string) =>
    request<void>(`/team/${id}`, { method: 'DELETE' }),
}

// ── Marketplace ─────────────────────────────────────────────────

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
