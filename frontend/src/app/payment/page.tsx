// app/checkout/page.jsx
import Checkout from '@/components/page'

export default function CheckoutPage() {
  // You can pass dynamic values here if needed.
  return (
    <div>
      <h1>Complete Your Payment</h1>
      <Checkout amount={2000} currency="usd" />
    </div>
  )
}