import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { fetchOrders } from '../lib/api'
import type { Order, OrderListResponse, OrderStatus } from '../types/order'
import { STATUS_LABELS } from '../types/order'
import { PriorityBadge, StatusBadge } from './StatusBadge'

const ALL_STATUSES: (OrderStatus | '')[] = ['', 'pendente', 'em_andamento', 'concluido', 'cancelado']

export default function OrderList() {
  const navigate = useNavigate()
  const [data, setData] = useState<OrderListResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState<OrderStatus | ''>('')
  const PAGE_SIZE = 20

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const params: Record<string, string | number> = { page, page_size: PAGE_SIZE }
      if (statusFilter) params.status = statusFilter
      setData(await fetchOrders(params))
    } catch {
      setError('Erro ao carregar pedidos.')
    } finally {
      setLoading(false)
    }
  }, [page, statusFilter])

  useEffect(() => { void load() }, [load])

  const totalPages = data ? Math.ceil(data.total_count / PAGE_SIZE) : 1

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
        <h1 style={{ fontSize: '22px', fontWeight: '700' }}>Pedidos</h1>
        <button className="btn-primary" onClick={() => navigate('novo')}>+ Novo Pedido</button>
      </div>

      {/* Status filter */}
      <div className="card" style={{ marginBottom: '16px', padding: '14px' }}>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {ALL_STATUSES.map((s) => (
            <button
              key={s}
              onClick={() => { setStatusFilter(s); setPage(1) }}
              style={{
                padding: '5px 14px', borderRadius: '20px', fontSize: '13px', fontWeight: '500',
                border: '1px solid', cursor: 'pointer',
                background: statusFilter === s ? 'var(--color-primary)' : 'white',
                color: statusFilter === s ? 'white' : 'var(--color-text)',
                borderColor: statusFilter === s ? 'var(--color-primary)' : 'var(--color-border)',
              }}
            >
              {s === '' ? 'Todos' : STATUS_LABELS[s]}
            </button>
          ))}
        </div>
      </div>

      <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
        {loading && (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '40px', gap: '10px', alignItems: 'center' }}>
            <span className="spinner spinner-dark" />
            <span style={{ color: 'var(--color-text-secondary)' }}>Carregando...</span>
          </div>
        )}
        {error && <div className="alert alert-error" style={{ margin: '16px' }}>{error}</div>}
        {!loading && !error && data && (
          data.items.length === 0 ? (
            <div style={{ padding: '48px', textAlign: 'center' }}>
              <p style={{ fontSize: '40px' }}>📭</p>
              <p style={{ color: 'var(--color-text-secondary)', marginTop: '8px' }}>Nenhum pedido encontrado.</p>
            </div>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Cliente</th><th>Descrição</th><th>Status</th>
                  <th>Prioridade</th><th style={{ textAlign: 'right' }}>Total</th><th></th>
                </tr>
              </thead>
              <tbody>
                {data.items.map((o: Order) => (
                  <tr key={o.id}>
                    <td><div style={{ fontWeight: '500' }}>{o.customer_name}</div><div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>{o.customer_email}</div></td>
                    <td style={{ maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{o.description}</td>
                    <td><StatusBadge status={o.status} /></td>
                    <td><PriorityBadge priority={o.priority} /></td>
                    <td style={{ textAlign: 'right', fontWeight: '600' }}>
                      {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(o.total_amount))}
                    </td>
                    <td>
                      <Link to={o.id}>
                        <button className="btn-secondary" style={{ padding: '4px 12px', fontSize: '12px' }}>Ver</button>
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )
        )}
        {data && data.total_count > PAGE_SIZE && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 20px', borderTop: '1px solid var(--color-border)' }}>
            <button onClick={() => setPage((p) => p - 1)} disabled={page === 1} className="btn-secondary" style={{ fontSize: '13px', padding: '6px 14px' }}>← Anterior</button>
            <span style={{ color: 'var(--color-text-secondary)', fontSize: '13px' }}>Página {page} de {totalPages}</span>
            <button onClick={() => setPage((p) => p + 1)} disabled={page >= totalPages} className="btn-secondary" style={{ fontSize: '13px', padding: '6px 14px' }}>Próxima →</button>
          </div>
        )}
      </div>
    </div>
  )
}
