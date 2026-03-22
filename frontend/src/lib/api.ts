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
    full_name: string
    phone?: string
    role: 'business' | 'consultant' | 'admin'
  }) => request<AuthResponse>('/auth/register', { method: 'POST', body: JSON.stringify(data) }),

  login: (data: { email: string; password: string }) =>
    request<AuthResponse>('/auth/login', { method: 'POST', body: JSON.stringify(data) }),

  me: () => request<UserResponse>('/auth/me'),
}

export interface UserResponse {
  id: string
  email: string
  full_name: string
  phone: string | null
  role: 'business' | 'consultant' | 'admin'
  is_active: boolean
  is_verified: boolean
  onboarding_complete: boolean
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: UserResponse
}
