"use client"

import React, { useEffect, useState } from "react"
import {
  EmbeddedCheckout,
  EmbeddedCheckoutProvider,
} from "@stripe/react-stripe-js"
import { loadStripe, Stripe } from "@stripe/stripe-js"

import { fetchClientSecret } from "../../actions/stripe"

const stripePromise = loadStripe(
  process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!
) as Promise<Stripe | null>

export default function Checkout(): React.ReactElement {
  const [clientSecret, setClientSecret] = useState<string | null>(null)

  useEffect(() => {
    fetchClientSecret().then(setClientSecret)
  }, [])

  if (!clientSecret) return <div>Loading...</div>

  return (
    <div id="checkout">
      <EmbeddedCheckoutProvider
        stripe={stripePromise}
        options={{ clientSecret }}
      >
        <EmbeddedCheckout />
      </EmbeddedCheckoutProvider>
    </div>
  )
}
