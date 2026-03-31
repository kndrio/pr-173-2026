import axios from 'axios'
import type { AuthTokenResponse, UserInfo } from '../types'

// Token stored only in module memory — never in localStorage
let _token: string | null = null

export function setAuthToken(token: string | null): void {
  _token = token
}

export function getAuthToken(): string | null {
  return _token
}

export const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  if (_token) {
    config.headers.Authorization = `Bearer ${_token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      setAuthToken(null)
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export async function loginUser(email: string, password: string): Promise<AuthTokenResponse> {
  const { data } = await api.post<AuthTokenResponse>('/auth/login', { email, password })
  return data
}

export async function registerUser(
  fullName: string,
  email: string,
  password: string,
): Promise<UserInfo> {
  const { data } = await api.post<UserInfo>('/auth/register', {
    full_name: fullName,
    email,
    password,
  })
  return data
}

export async function getMe(): Promise<UserInfo> {
  const { data } = await api.get<UserInfo>('/users/me')
  return data
}
