import React, { useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { getAuthToken, loginUser, setAuthToken } from './lib/api'
import OrderDetail from './components/OrderDetail'
import OrderForm from './components/OrderForm'
import OrderList from './components/OrderList'
import axios from 'axios'

function MiniLogin({ onLogin }: { onLogin: () => void }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const { access_token } = await loginUser(email, password)
      setAuthToken(access_token)
      onLogin()
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail ?? 'Credenciais inválidas')
      } else {
        setError('Erro ao autenticar')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={styles.loginPage}>
      <div style={styles.loginCard}>
        <h1 style={{ fontSize: '20px', marginBottom: '4px' }}>Orders MFE</h1>
        <p style={{ color: 'var(--color-text-secondary)', fontSize: '13px', marginBottom: '24px' }}>
          App standalone de Pedidos
        </p>
        {error && <div className="alert alert-error">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>E-mail</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div className="form-group">
            <label>Senha</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          <button type="submit" className="btn-primary" disabled={loading} style={{ width: '100%', marginTop: '8px' }}>
            {loading ? <span className="spinner" /> : 'Entrar'}
          </button>
        </form>
      </div>
    </div>
  )
}

function AppShell() {
  const navigate = useNavigate()

  function handleLogout() {
    setAuthToken(null)
    navigate('/', { replace: true })
  }

  return (
    <div style={styles.root}>
      <header style={styles.header}>
        <span style={{ fontWeight: '700', fontSize: '15px', color: 'white' }}>
          📋 Orders MFE <span style={{ fontSize: '11px', opacity: 0.7 }}>(standalone)</span>
        </span>
        <button onClick={handleLogout} style={styles.logoutBtn}>Sair</button>
      </header>
      <main style={styles.main}>
        <Routes>
          <Route path="/" element={<OrderList />} />
          <Route path="/novo" element={<OrderForm />} />
          <Route path="/:id" element={<OrderDetail />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  const [authenticated, setAuthenticated] = useState(() => !!getAuthToken())

  if (!authenticated) {
    return (
      <>
        <link rel="stylesheet" href="/src/index.css" />
        <MiniLogin onLogin={() => setAuthenticated(true)} />
      </>
    )
  }

  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  )
}

const styles: Record<string, React.CSSProperties> = {
  loginPage: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #0c326f 0%, #1351b4 100%)',
    padding: '24px',
  },
  loginCard: {
    background: 'white',
    borderRadius: '8px',
    padding: '32px',
    width: '100%',
    maxWidth: '360px',
    boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
  },
  root: {
    display: 'flex',
    flexDirection: 'column',
    minHeight: '100vh',
  },
  header: {
    background: 'var(--color-primary)',
    color: 'white',
    padding: '0 24px',
    height: '48px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  logoutBtn: {
    background: 'rgba(255,255,255,0.15)',
    color: 'white',
    border: '1px solid rgba(255,255,255,0.3)',
    borderRadius: '4px',
    padding: '5px 12px',
    fontSize: '13px',
    cursor: 'pointer',
  },
  main: {
    flex: 1,
    padding: '24px',
    maxWidth: '1200px',
    width: '100%',
    margin: '0 auto',
  },
}
