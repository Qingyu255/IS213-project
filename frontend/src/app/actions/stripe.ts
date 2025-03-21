'use server'

import { headers } from 'next/headers'
import { Stripe } from 'stripe'

import { stripe } from '../../lib/stripe'

export async function fetchClientSecret(): Promise<string | null> {
  const origin = (await headers()).get('origin')
  
  if (!origin) {
    throw new Error('Origin header is required')
  }

  // Create Checkout Sessions from body params.
  const session: Stripe.Checkout.Session = await stripe.checkout.sessions.create({
    ui_mode: 'embedded',
    line_items: [
      {
        // Provide the exact Price ID (for example, pr_1234) of
        // the product you want to sell
        price: '{{PRICE_ID}}',
        quantity: 1
      }
    ],
    mode: 'payment',
    return_url: `${origin}/return?session_id={CHECKOUT_SESSION_ID}`,
  })

  return session.client_secret
}