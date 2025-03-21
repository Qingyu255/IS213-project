'use client'

import { useState, useEffect } from 'react'
import { EmbeddedCheckout, EmbeddedCheckoutProvider } from '@stripe/react-stripe-js'
import { loadStripe } from '@stripe/stripe-js'

// Load Stripe with your publishable key and any required beta flags.
const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY, {
  betas: ['custom_checkout_beta_5']
})

export default function Checkout() {
  const [clientSecret, setClientSecret] = useState(null)

  // When the component mounts, call the backend endpoint to create a Checkout Session.
  useEffect(() => {
    // Example: Sending a POST request to /api/payment with dynamic pricing parameters.
    fetch('/api/payment', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      // Pass the dynamic price (in cents) and currency
      body: JSON.stringify({ amount: 1000, currency: 'usd' })
    })
      .then(response => response.json())
      .then(data => {
        if (data.clientSecret) {
          setClientSecret(data.clientSecret)
        } else {
          console.error('Error fetching client secret:', data)
        }
      })
      .catch(error => console.error('Fetch error:', error))
  }, [])

  if (!clientSecret) return <div>Loading checkout...</div>

  return (
    <div id="checkout">
      <EmbeddedCheckoutProvider stripe={stripePromise} options={{ clientSecret }}>
        <EmbeddedCheckout />
      </EmbeddedCheckoutProvider>
    </div>
  )
}

