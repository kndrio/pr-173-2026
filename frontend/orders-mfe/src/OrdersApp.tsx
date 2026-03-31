import { useEffect } from 'react'
import { Route, Routes } from 'react-router-dom'
import { setAuthToken } from './lib/api'
import OrderDetail from './components/OrderDetail'
import OrderForm from './components/OrderForm'
import OrderList from './components/OrderList'

interface OrdersAppProps {
  token: string
}

/**
 * Federated entry point consumed by the Shell HOST via Module Federation.
 * Does NOT include <BrowserRouter> — relies on Shell's router context.
 * Receives the JWT token as a prop and injects it into the orders API client.
 */
export default function OrdersApp({ token }: OrdersAppProps) {
  useEffect(() => {
    setAuthToken(token)
  }, [token])

  return (
    <Routes>
      <Route index element={<OrderList />} />
      <Route path="novo" element={<OrderForm />} />
      <Route path=":id" element={<OrderDetail />} />
    </Routes>
  )
}
