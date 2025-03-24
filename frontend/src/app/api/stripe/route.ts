import { NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';

export async function POST(request: Request) {
  try {
    if (!stripe) {
      throw new Error('Stripe is not initialized');
    }

    // Get the request data
    const data = await request.json();
    const { eventId, amount, description } = data;

    if (!eventId || !amount) {
      return NextResponse.json(
        { error: 'Missing required parameters' },
        { status: 400 }
      );
    }

    // Determine the origin for success and cancel URLs
    const origin = request.headers.get('origin') || 'http://localhost:3000';

    // Create a checkout session
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      line_items: [
        {
          price_data: {
            currency: 'sgd',
            product_data: {
              name: 'Event Creation Fee',
              description: description || 'Fee for creating a new event',
            },
            unit_amount: amount, // Amount in cents
          },
          quantity: 1,
        },
      ],
      metadata: {
        event_id: eventId,
      },
      mode: 'payment',
      success_url: `${origin}/create/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${origin}/create?canceled=true`,
    });

    if (!session.url) {
      throw new Error('Failed to create checkout session URL');
    }

    return NextResponse.json({ url: session.url });
  } catch (error) {
    console.error('Error creating checkout session:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'An unknown error occurred' },
      { status: 500 }
    );
  }
} 