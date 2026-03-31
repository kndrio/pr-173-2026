declare module 'ordersApp/OrdersApp' {
  import type { ComponentType } from 'react'

  interface OrdersAppProps {
    token: string
  }

  const OrdersApp: ComponentType<OrdersAppProps>
  export default OrdersApp
}
