import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createOrder } from '../lib/api'
import type { Priority } from '../types/order'
import { PRIORITY_LABELS } from '../types/order'
import axios from 'axios'

interface Item { name: string; quantity: string; unit_price: string }
const emptyItem = (): Item => ({ name: '', quantity: '1', unit_price: '' })

export default function OrderForm() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [form, setForm] = useState({ customer_name: '', customer_email: '', description: '', priority: 'media' as Priority, notes: '' })
  const [items, setItems] = useState<Item[]>([emptyItem()])

  function handleChange(e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }))
  }

  function handleItem(i: number, f: keyof Item, v: string) {
    setItems((prev) => prev.map((it, idx) => idx === i ? { ...it, [f]: v } : it))
  }

  const total = items.reduce((s, it) => s + (Number(it.quantity) || 0) * (Number(it.unit_price) || 0), 0)
  const fmt = (v: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const valid = items.filter((it) => it.name && Number(it.quantity) > 0 && Number(it.unit_price) > 0)
    if (valid.length === 0) { setError('Adicione pelo menos um item.'); return }
    setLoading(true)
    try {
      const o = await createOrder({ ...form, items: valid.map((it) => ({ name: it.name, quantity: Number(it.quantity), unit_price: Number(it.unit_price).toFixed(2) })) })
      navigate(`../${o.id}`)
    } catch (err) {
      setError(axios.isAxiosError(err) ? (err.response?.data?.detail ?? 'Erro ao criar pedido') : 'Erro inesperado')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
        <h1 style={{ fontSize: '22px', fontWeight: '700' }}>Novo Pedido</h1>
        <button onClick={() => navigate('..')} className="btn-secondary">← Voltar</button>
      </div>
      {error && <div className="alert alert-error">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="card" style={{ marginBottom: '16px' }}>
          <h2 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '16px' }}>Dados do Cliente</h2>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group"><label>Nome do cliente *</label><input name="customer_name" value={form.customer_name} onChange={handleChange} required /></div>
            <div className="form-group"><label>E-mail *</label><input name="customer_email" type="email" value={form.customer_email} onChange={handleChange} required /></div>
          </div>
          <div className="form-group"><label>Descrição *</label><textarea name="description" value={form.description} onChange={handleChange} rows={2} required style={{ resize: 'vertical' }} /></div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group">
              <label>Prioridade</label>
              <select name="priority" value={form.priority} onChange={handleChange}>
                {(Object.keys(PRIORITY_LABELS) as Priority[]).map((p) => <option key={p} value={p}>{PRIORITY_LABELS[p]}</option>)}
              </select>
            </div>
            <div className="form-group"><label>Observações</label><textarea name="notes" value={form.notes} onChange={handleChange} rows={2} style={{ resize: 'vertical' }} /></div>
          </div>
        </div>

        <div className="card" style={{ marginBottom: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: '600' }}>Itens</h2>
            <button type="button" onClick={() => setItems((p) => [...p, emptyItem()])} className="btn-secondary" style={{ fontSize: '13px', padding: '5px 12px' }}>+ Item</button>
          </div>
          {items.map((it, i) => (
            <div key={i} style={{ display: 'flex', gap: '10px', marginBottom: '10px', alignItems: 'flex-end' }}>
              <div style={{ flex: 3 }}><label>Nome</label><input value={it.name} onChange={(e) => handleItem(i, 'name', e.target.value)} placeholder="Produto A" /></div>
              <div style={{ flex: 1 }}><label>Qtd</label><input type="number" min="1" value={it.quantity} onChange={(e) => handleItem(i, 'quantity', e.target.value)} /></div>
              <div style={{ flex: 2 }}><label>Preço (R$)</label><input type="number" min="0.01" step="0.01" value={it.unit_price} onChange={(e) => handleItem(i, 'unit_price', e.target.value)} /></div>
              <div style={{ flex: 1, textAlign: 'right', fontWeight: '600', paddingBottom: '8px' }}>{fmt((Number(it.quantity)||0)*(Number(it.unit_price)||0))}</div>
              <button type="button" onClick={() => setItems((p) => p.filter((_,j)=>j!==i))} disabled={items.length===1} className="btn-danger" style={{ padding: '8px 10px', marginBottom: '0' }}>×</button>
            </div>
          ))}
          <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '12px', borderTop: '2px solid var(--color-border)' }}>
            <span style={{ fontWeight: '600' }}>Total</span>
            <span style={{ fontSize: '20px', fontWeight: '700', color: 'var(--color-primary)' }}>{fmt(total)}</span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
          <button type="button" onClick={() => navigate('..')} className="btn-secondary">Cancelar</button>
          <button type="submit" className="btn-primary" disabled={loading} style={{ minWidth: '140px' }}>
            {loading ? <span className="spinner" /> : 'Criar Pedido'}
          </button>
        </div>
      </form>
    </div>
  )
}
