import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import axios from 'axios'

export default function LoginPage() {
  const { login, register } = useAuth()
  const navigate = useNavigate()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [form, setForm] = useState({ fullName: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState('')

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }))
    setError('')
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      if (mode === 'login') {
        await login(form.email, form.password)
        navigate('/pedidos')
      } else {
        await register(form.fullName, form.email, form.password)
        setSuccess('Conta criada com sucesso! Faça login.')
        setMode('login')
        setForm((f) => ({ ...f, fullName: '', password: '' }))
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const detail = err.response?.data?.detail
        setError(typeof detail === 'string' ? detail : 'Credenciais inválidas.')
      } else {
        setError('Erro inesperado. Tente novamente.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        {/* Header */}
        <div style={styles.header}>
          <div style={styles.logo}>
            <span style={styles.logoIcon}>🇧🇷</span>
          </div>
          <h1 style={styles.title}>Gestão de Pedidos</h1>
          <p style={styles.subtitle}>Sistema Interno — Plataforma de Pedidos</p>
        </div>

        <div className="card" style={styles.card}>
          <h2 style={styles.formTitle}>
            {mode === 'login' ? 'Entrar na conta' : 'Criar conta'}
          </h2>

          {error && <div className="alert alert-error">{error}</div>}
          {success && <div className="alert alert-success">{success}</div>}

          <form onSubmit={handleSubmit}>
            {mode === 'register' && (
              <div className="form-group">
                <label htmlFor="fullName">Nome completo</label>
                <input
                  id="fullName"
                  name="fullName"
                  type="text"
                  value={form.fullName}
                  onChange={handleChange}
                  placeholder="Seu nome completo"
                  required
                  autoComplete="name"
                />
              </div>
            )}

            <div className="form-group">
              <label htmlFor="email">E-mail</label>
              <input
                id="email"
                name="email"
                type="email"
                value={form.email}
                onChange={handleChange}
                placeholder="seu@email.gov.br"
                required
                autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Senha</label>
              <input
                id="password"
                name="password"
                type="password"
                value={form.password}
                onChange={handleChange}
                placeholder="••••••••"
                required
                minLength={8}
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              />
            </div>

            <button
              type="submit"
              className="btn-primary"
              style={styles.submitBtn}
              disabled={loading}
            >
              {loading ? <span className="spinner" /> : mode === 'login' ? 'Entrar' : 'Criar conta'}
            </button>
          </form>

          <div style={styles.toggle}>
            {mode === 'login' ? (
              <>
                Não tem conta?{' '}
                <button
                  type="button"
                  onClick={() => { setMode('register'); setError('') }}
                  style={styles.linkBtn}
                >
                  Criar conta
                </button>
              </>
            ) : (
              <>
                Já tem conta?{' '}
                <button
                  type="button"
                  onClick={() => { setMode('login'); setError('') }}
                  style={styles.linkBtn}
                >
                  Entrar
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #0c326f 0%, #1351b4 100%)',
    padding: '24px',
  },
  container: {
    width: '100%',
    maxWidth: '420px',
  },
  header: {
    textAlign: 'center',
    marginBottom: '32px',
  },
  logo: {
    fontSize: '40px',
    marginBottom: '12px',
  },
  logoIcon: {},
  title: {
    color: 'white',
    fontSize: '24px',
    fontWeight: '700',
    marginBottom: '4px',
  },
  subtitle: {
    color: 'rgba(255,255,255,0.7)',
    fontSize: '13px',
  },
  card: {
    borderRadius: '8px',
  },
  formTitle: {
    fontSize: '18px',
    fontWeight: '600',
    marginBottom: '20px',
    color: 'var(--color-text)',
  },
  submitBtn: {
    width: '100%',
    padding: '12px',
    fontSize: '15px',
    marginTop: '8px',
  },
  toggle: {
    marginTop: '20px',
    textAlign: 'center',
    fontSize: '13px',
    color: 'var(--color-text-secondary)',
  },
  linkBtn: {
    background: 'none',
    border: 'none',
    color: 'var(--color-primary)',
    fontWeight: '600',
    padding: '0',
    cursor: 'pointer',
    fontSize: '13px',
  },
}
