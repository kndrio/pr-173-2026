import React from 'react'
import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div style={styles.root}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <Link to="/pedidos" style={styles.brand}>
            <span style={{ fontSize: '20px' }}>📋</span>
            <span style={styles.brandName}>Gestão de Pedidos</span>
          </Link>
          <div style={styles.headerRight}>
            <span style={styles.userName}>
              {user?.full_name ?? user?.email}
            </span>
            <span style={styles.userRole}>{user?.role}</span>
            <button onClick={handleLogout} className="btn-secondary" style={styles.logoutBtn}>
              Sair
            </button>
          </div>
        </div>
      </header>

      <div style={styles.body}>
        {/* Sidebar */}
        <nav style={styles.sidebar}>
          <ul style={styles.navList}>
            <li>
              <NavLink
                to="/pedidos"
                style={({ isActive }) => ({
                  ...styles.navLink,
                  ...(isActive ? styles.navLinkActive : {}),
                })}
              >
                <span>📋</span> Pedidos
              </NavLink>
            </li>
          </ul>
        </nav>

        {/* Content */}
        <main style={styles.main}>
          <Outlet />
        </main>
      </div>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  root: {
    display: 'flex',
    flexDirection: 'column',
    minHeight: '100vh',
  },
  header: {
    background: 'var(--color-primary)',
    color: 'white',
    boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
    position: 'sticky',
    top: 0,
    zIndex: 100,
  },
  headerContent: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 24px',
    height: '56px',
    maxWidth: '1400px',
    margin: '0 auto',
    width: '100%',
  },
  brand: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    textDecoration: 'none',
    color: 'white',
  },
  brandName: {
    fontSize: '16px',
    fontWeight: '700',
    letterSpacing: '0.3px',
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  userName: {
    fontSize: '14px',
    fontWeight: '500',
    color: 'rgba(255,255,255,0.9)',
  },
  userRole: {
    fontSize: '11px',
    background: 'rgba(255,255,255,0.2)',
    padding: '2px 8px',
    borderRadius: '12px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    color: 'white',
  },
  logoutBtn: {
    background: 'rgba(255,255,255,0.15)',
    color: 'white',
    border: '1px solid rgba(255,255,255,0.3)',
    fontSize: '13px',
    padding: '6px 14px',
  },
  body: {
    display: 'flex',
    flex: 1,
  },
  sidebar: {
    width: '220px',
    background: 'var(--color-surface)',
    borderRight: '1px solid var(--color-border)',
    padding: '16px 0',
    flexShrink: 0,
  },
  navList: {
    listStyle: 'none',
  },
  navLink: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '10px 20px',
    color: 'var(--color-text)',
    textDecoration: 'none',
    fontSize: '14px',
    fontWeight: '500',
    borderLeft: '3px solid transparent',
    transition: 'all 0.15s',
  },
  navLinkActive: {
    color: 'var(--color-primary)',
    borderLeftColor: 'var(--color-primary)',
    background: 'rgba(19, 81, 180, 0.06)',
  },
  main: {
    flex: 1,
    padding: '24px',
    overflow: 'auto',
    maxWidth: '1200px',
  },
}
