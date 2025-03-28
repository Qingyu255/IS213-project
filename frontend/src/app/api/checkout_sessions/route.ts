/* eslint-disable @typescript-eslint/no-explicit-any */
import { NextResponse } from 'next/server'
import { headers } from 'next/headers'

import { stripe } from '../../../lib/stripe'

export async function POST() {
  try {
    const headersList = await headers()
    const origin = headersList.get('origin')

    // Create Checkout Sessions from body params.
    const session = await stripe.checkout.sessions.create({
      line_items: [
        {
          // For one-time payments, we can specify price data directly instead of using a Price ID
          price_data: {
            currency: 'sgd',
            product_data: {
              name: 'Event Creation Fee',
              description: 'One-time fee for creating an event'
            },
            unit_amount: 200, // Amount in cents (SGD 2.00)
          },
          quantity: 1,
        },
      ],
      mode: 'payment',
      success_url: `${origin}/create/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${origin}/?canceled=true`,
    });
    
    if (!session.url) {
      throw new Error('Failed to create checkout session URL');
    }
    
    return NextResponse.redirect(session.url, 303)
  } catch (err: any) {
    return NextResponse.json(
      { error: err.message },
      { status: err.statusCode || 500 }
    )
  }
}