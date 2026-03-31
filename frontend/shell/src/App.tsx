import { Suspense, lazy } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import { getAuthToken } from './lib/api'

// Lazy-load the Orders MFE remote via Module Federation
const RemoteOrdersApp = lazy(() => import('ordersApp/OrdersApp'))

function OrdersLoader() {
  return (
    <Suspense
      fallback={
        <div style={{ display: 'flex', justifyContent: 'center', padding: '60px' }}>
          <span className="spinner spinner-dark" />
        </div>
      }
    >
      <RemoteOrdersApp token={getAuthToken() ?? ''} />
    </Suspense>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/pedidos" replace />} />
            {/* All /pedidos/* routes are handled by the Orders MFE remote */}
            <Route path="pedidos/*" element={<OrdersLoader />} />
          </Route>
          <Route path="*" element={<Navigate to="/pedidos" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
