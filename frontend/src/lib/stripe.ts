import Stripe from 'stripe'

// Make sure the secret is available
if (typeof window === 'undefined' && !process.env.STRIPE_SECRET_KEY) {
  throw new Error('STRIPE_SECRET_KEY is not set. Please add it to your .env file')
}

// We only create the Stripe instance on the server
// This prevents client-side code from trying to access the secret
let stripe: Stripe | null = null;

if (typeof window === 'undefined') {
  stripe = new Stripe(process.env.STRIPE_SECRET_KEY as string, {
    apiVersion: '2025-02-24.acacia' as Stripe.LatestApiVersion, // Match the type definition
  })
}

export { stripe } 