import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { fetchOrder, updateOrder } from '../lib/api'
import type { Order, OrderStatus } from '../types/order'
import { STATUS_LABELS, VALID_TRANSITIONS } from '../types/order'
import { PriorityBadge, StatusBadge } from './StatusBadge'

const fmt = (v: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v)
const fmtDate = (iso: string) => new Date(iso).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })

export default function OrderDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [updating, setUpdating] = useState(false)

  const load = useCallback(async () => {
    if (!id) return
    setLoading(true)
    try { setOrder(await fetchOrder(id)) } catch { setError('Pedido não encontrado.') } finally { setLoading(false) }
  }, [id])

  useEffect(() => { void load() }, [load])

  async function handleStatus(s: OrderStatus) {
    if (!id) return
    setUpdating(true)
    try { setOrder(await updateOrder(id, { status: s })) } catch { setError('Erro ao atualizar.') } finally { setUpdating(false) }
  }

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '60px' }}><span className="spinner spinner-dark" /></div>
  if (error || !order) return <div><div className="alert alert-error">{error || 'Não encontrado'}</div><button onClick={() => navigate('..')} className="btn-secondary">← Voltar</button></div>

  const transitions = VALID_TRANSITIONS[order.status]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px', alignItems: 'flex-start' }}>
        <div>
          <button onClick={() => navigate('..')} className="btn-secondary" style={{ marginBottom: '8px', fontSize: '13px' }}>← Voltar</button>
          <h1 style={{ fontSize: '20px', fontWeight: '700' }}>Pedido #{order.id.slice(0,8)}</h1>
        </div>
        <StatusBadge status={order.status} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', alignItems: 'start' }}>
        <div>
          <div className="card" style={{ marginBottom: '16px' }}>
            <h2 style={{ fontSize: '15px', fontWeight: '600', marginBottom: '12px' }}>Dados do Cliente</h2>
            <p><strong>Nome:</strong> {order.customer_name}</p>
            <p style={{ marginTop: '6px' }}><strong>E-mail:</strong> {order.customer_email}</p>
          </div>
          <div className="card" style={{ marginBottom: '16px' }}>
            <h2 style={{ fontSize: '15px', fontWeight: '600', marginBottom: '12px' }}>Informações</h2>
            <p><strong>Status:</strong> <StatusBadge status={order.status} /></p>
            <p style={{ marginTop: '8px' }}><strong>Prioridade:</strong> <PriorityBadge priority={order.priority} /></p>
            <p style={{ marginTop: '8px' }}><strong>Descrição:</strong> {order.description}</p>
            {order.notes && <p style={{ marginTop: '8px' }}><strong>Obs:</strong> {order.notes}</p>}
            <p style={{ marginTop: '8px', color: 'var(--color-text-secondary)', fontSize: '12px' }}>Criado: {fmtDate(order.created_at)}</p>
          </div>
          {transitions.length > 0 && (
            <div className="card" style={{ marginBottom: '16px' }}>
              <h2 style={{ fontSize: '15px', fontWeight: '600', marginBottom: '12px' }}>Atualizar Status</h2>
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                {transitions.map((t) => (
                  <button key={t} onClick={() => void handleStatus(t)} disabled={updating} className={t === 'cancelado' ? 'btn-danger' : t === 'concluido' ? 'btn-success' : 'btn-primary'}>
                    {updating ? <span className="spinner" style={{ width: '14px', height: '14px' }} /> : STATUS_LABELS[t]}
                  </button>
                ))}
              </div>
            </div>
          )}
          <div className="card" style={{ background: '#f5f0ff', border: '1px solid #c4a8ff' }}>
            <h2 style={{ fontSize: '15px', fontWeight: '600', marginBottom: '8px', color: '#6b35d1' }}>Analisar com IA</h2>
            <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '10px' }}>Claude AI — análise de prioridade e resumo executivo.</p>
            <button disabled style={{ background: '#c4a8ff', color: 'white', border: 'none', padding: '6px 14px', borderRadius: '4px', cursor: 'not-allowed', opacity: 0.7, fontSize: '13px' }}>🤖 Analisar (Fase 5)</button>
          </div>
        </div>

        <div className="card">
          <h2 style={{ fontSize: '15px', fontWeight: '600', marginBottom: '12px' }}>Itens</h2>
          <table>
            <thead><tr><th>Item</th><th style={{ textAlign: 'right' }}>Qtd</th><th style={{ textAlign: 'right' }}>Unit.</th><th style={{ textAlign: 'right' }}>Subtotal</th></tr></thead>
            <tbody>
              {order.items.map((it, i) => (
                <tr key={i}>
                  <td>{it.name}</td>
                  <td style={{ textAlign: 'right' }}>{it.quantity}</td>
                  <td style={{ textAlign: 'right' }}>{fmt(Number(it.unit_price))}</td>
                  <td style={{ textAlign: 'right', fontWeight: '600' }}>{fmt(it.quantity * Number(it.unit_price))}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '12px', borderTop: '2px solid var(--color-border)', marginTop: '4px' }}>
            <span style={{ fontWeight: '600' }}>Total</span>
            <span style={{ fontSize: '22px', fontWeight: '700', color: 'var(--color-primary)' }}>{fmt(Number(order.total_amount))}</span>
          </div>
        </div>
      </div>
    </div>
  )
}
