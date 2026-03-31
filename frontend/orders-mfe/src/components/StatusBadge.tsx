import type { OrderStatus, Priority } from '../types/order'
import { PRIORITY_LABELS, STATUS_LABELS } from '../types/order'

const STATUS_STYLES: Record<OrderStatus, React.CSSProperties> = {
  pendente: { color: '#7a5800', background: 'var(--status-pendente-bg)', border: '1px solid var(--status-pendente)' },
  em_andamento: { color: '#0c3b8f', background: 'var(--status-em-andamento-bg)', border: '1px solid var(--status-em-andamento)' },
  concluido: { color: '#0a4e12', background: 'var(--status-concluido-bg)', border: '1px solid var(--status-concluido)' },
  cancelado: { color: '#8b1203', background: 'var(--status-cancelado-bg)', border: '1px solid var(--status-cancelado)' },
}

const PRIORITY_STYLES: Record<Priority, React.CSSProperties> = {
  baixa: { color: '#636363', background: '#f0f0f0', border: '1px solid #d4d4d4' },
  media: { color: '#0c3b8f', background: '#d4e4ff', border: '1px solid #155bcb' },
  alta: { color: '#7a5800', background: '#fff5cc', border: '1px solid #f0ad00' },
  urgente: { color: '#8b1203', background: '#fde0dc', border: '1px solid #e52207' },
}

const base: React.CSSProperties = {
  display: 'inline-block', padding: '3px 10px', borderRadius: '12px',
  fontSize: '11px', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.4px', whiteSpace: 'nowrap',
}

export function StatusBadge({ status }: { status: OrderStatus }) {
  return <span style={{ ...base, ...STATUS_STYLES[status] }}>{STATUS_LABELS[status]}</span>
}

export function PriorityBadge({ priority }: { priority: Priority }) {
  return <span style={{ ...base, ...PRIORITY_STYLES[priority] }}>{PRIORITY_LABELS[priority]}</span>
}
