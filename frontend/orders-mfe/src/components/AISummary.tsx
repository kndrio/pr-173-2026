import { useState } from 'react'
import { analyzeOrder } from '../lib/api'
import type { AIAnalysisResponse } from '../lib/api'

const PRIORITY_COLORS: Record<string, string> = {
  baixa: '#6b9e3d',
  media: '#e6a817',
  alta: '#d97706',
  urgente: '#dc2626',
}

interface Props {
  orderId: string
}

export default function AISummary({ orderId }: Props) {
  const [result, setResult] = useState<AIAnalysisResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleAnalyze() {
    setLoading(true)
    setError('')
    try {
      setResult(await analyzeOrder(orderId))
    } catch {
      setError('Não foi possível concluir a análise.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card" style={{ background: '#f5f0ff', border: '1px solid #c4a8ff' }}>
      <h2 style={{ fontSize: '15px', fontWeight: '600', marginBottom: '8px', color: '#6b35d1' }}>
        Analisar com IA
      </h2>
      <p style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '10px' }}>
        Claude AI — análise de prioridade e resumo executivo.
      </p>

      {!result && (
        <button
          onClick={() => void handleAnalyze()}
          disabled={loading}
          style={{
            background: loading ? '#c4a8ff' : '#6b35d1',
            color: 'white',
            border: 'none',
            padding: '6px 14px',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontSize: '13px',
          }}
        >
          {loading ? 'Analisando pedido...' : '🤖 Analisar com IA'}
        </button>
      )}

      {error && (
        <p style={{ color: '#dc2626', fontSize: '13px', marginTop: '8px' }}>{error}</p>
      )}

      {result && (
        <div style={{ marginTop: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
            <span
              style={{
                fontSize: '12px',
                fontWeight: '700',
                padding: '2px 8px',
                borderRadius: '4px',
                background: PRIORITY_COLORS[result.suggested_priority] ?? '#888',
                color: 'white',
              }}
            >
              Prioridade sugerida: {result.suggested_priority.toUpperCase()}
            </span>
            {result.model_used === 'rule-based-fallback' && (
              <span style={{ fontSize: '11px', color: '#888', fontStyle: 'italic' }}>
                Análise por regras
              </span>
            )}
          </div>
          <p style={{ fontSize: '13px', marginBottom: '8px' }}>{result.executive_summary}</p>
          {result.observations.length > 0 && (
            <ul style={{ paddingLeft: '16px', margin: 0 }}>
              {result.observations.map((obs, i) => (
                <li key={i} style={{ fontSize: '12px', color: 'var(--color-text-secondary)', marginBottom: '4px' }}>
                  {obs}
                </li>
              ))}
            </ul>
          )}
          <button
            onClick={() => void handleAnalyze()}
            style={{
              marginTop: '10px',
              background: 'transparent',
              border: '1px solid #c4a8ff',
              color: '#6b35d1',
              padding: '4px 10px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px',
            }}
          >
            Reanalisar
          </button>
        </div>
      )}
    </div>
  )
}
