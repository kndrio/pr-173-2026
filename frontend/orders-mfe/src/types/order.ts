export type OrderStatus = 'pendente' | 'em_andamento' | 'concluido' | 'cancelado'
export type Priority = 'baixa' | 'media' | 'alta' | 'urgente'

export interface OrderItem {
  name: string
  quantity: number
  unit_price: string
}

export interface Order {
  id: string
  customer_name: string
  customer_email: string
  description: string
  items: OrderItem[]
  total_amount: string
  status: OrderStatus
  priority: Priority
  notes: string | null
  created_by: string
  created_at: string
  updated_at: string
}

export interface OrderListResponse {
  items: Order[]
  total_count: number
  page: number
  page_size: number
}

export interface CreateOrderPayload {
  customer_name: string
  customer_email: string
  description: string
  items: { name: string; quantity: number; unit_price: string }[]
  priority: Priority
  notes?: string
}

export interface UpdateOrderPayload {
  status?: OrderStatus
  priority?: Priority
  notes?: string
}

export const VALID_TRANSITIONS: Record<OrderStatus, OrderStatus[]> = {
  pendente: ['em_andamento', 'cancelado'],
  em_andamento: ['concluido', 'cancelado'],
  concluido: [],
  cancelado: [],
}

export const STATUS_LABELS: Record<OrderStatus, string> = {
  pendente: 'Pendente',
  em_andamento: 'Em Andamento',
  concluido: 'Concluído',
  cancelado: 'Cancelado',
}

export const PRIORITY_LABELS: Record<Priority, string> = {
  baixa: 'Baixa',
  media: 'Média',
  alta: 'Alta',
  urgente: 'Urgente',
}
