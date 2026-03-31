import axios from 'axios'
import type {
  CreateOrderPayload,
  Order,
  OrderListResponse,
  UpdateOrderPayload,
} from '../types/order'

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
    if (axios.isAxiosError(error)) {
      const status = error.response?.status
      if (status === 401) {
        setAuthToken(null)
        // Redirect to Shell login (works in both standalone and federated modes)
        window.location.href = '/login'
      } else if (status !== undefined && status >= 500) {
        // Preserve the AxiosError so axios.isAxiosError() still returns true downstream;
        // attach a user-friendly message for components to display.
        Object.assign(error, { userMessage: 'Erro no servidor. Tente novamente mais tarde.' })
      }
    }
    return Promise.reject(error)
  },
)

export interface LoginResponse {
  access_token: string
  token_type: string
}

export async function loginUser(email: string, password: string): Promise<LoginResponse> {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  const { data } = await api.post<LoginResponse>('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return data
}

export async function fetchOrders(params: {
  page?: number
  page_size?: number
  status?: string
  priority?: string
}): Promise<OrderListResponse> {
  const { data } = await api.get<OrderListResponse>('/orders/pedidos', { params })
  return data
}

export async function fetchOrder(id: string): Promise<Order> {
  const { data } = await api.get<Order>(`/orders/pedidos/${id}`)
  return data
}

export async function createOrder(payload: CreateOrderPayload): Promise<Order> {
  const { data } = await api.post<Order>('/orders/pedidos', payload)
  return data
}

export async function updateOrder(id: string, payload: UpdateOrderPayload): Promise<Order> {
  const { data } = await api.patch<Order>(`/orders/pedidos/${id}`, payload)
  return data
}

export interface AIAnalysisResponse {
  suggested_priority: string
  executive_summary: string
  observations: string[]
  model_used: string
  analyzed_at: string
}

export async function analyzeOrder(id: string): Promise<AIAnalysisResponse> {
  const { data } = await api.post<AIAnalysisResponse>(`/orders/pedidos/${id}/ai-analysis`)
  return data
}
