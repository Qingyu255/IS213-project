'use server'

import { stripe } from '@/lib/stripe'
// We still need Stripe for type definitions
import type Stripe from 'stripe'

type CheckoutSessionResponse = {
  success: boolean;
  session?: {
    id: string;
    status: string | null;
    amount_total?: number | null;
    payment_status?: string | null;
    customer_details?: {
      email?: string | null;
      name?: string | null;
    };
    metadata?: Record<string, string> | null;
  };
  error?: string;
}

/**
 * Retrieves a Stripe checkout session by its ID
 * This is a server action that can be called from client components
 */
export async function getCheckoutSession(sessionId: string): Promise<CheckoutSessionResponse> {
  try {
    if (!stripe) {
      return {
        success: false,
        error: 'Stripe is not initialized'
      }
    }
    
    const session = await stripe.checkout.sessions.retrieve(sessionId, {
      expand: ['line_items', 'payment_intent']
    })
    
    // Extract only the serializable data we need
    const serializedSession = {
      id: session.id,
      status: session.status,
      amount_total: session.amount_total,
      payment_status: session.payment_status,
      customer_details: {
        email: session.customer_details?.email,
        name: session.customer_details?.name
      },
      metadata: session.metadata
    }
    
    return {
      success: true,
      session: serializedSession
    }
  } catch (error) {
    console.error('Error retrieving checkout session:', error)
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to retrieve checkout session'
    }
  }
} 