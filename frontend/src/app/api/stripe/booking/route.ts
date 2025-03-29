import { NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';

export async function POST(request: Request) {
  try {
    if (!stripe) {
      throw new Error('Stripe is not initialized');
    }

    // Get the request data
    const data = await request.json();
    const { bookingId, amount, eventTitle, quantity, successUrl } = data;

    if (!bookingId || !amount) {
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
              name: eventTitle || 'Event Ticket',
              description: `Booking for ${quantity} ticket${quantity > 1 ? 's' : ''}`,
            },
            unit_amount: amount, // Amount in cents
          },
          quantity: 1,
        },
      ],
      metadata: {
        booking_id: bookingId,
      },
      mode: 'payment',
      success_url: successUrl || `${origin}/book/${bookingId}/success?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${origin}/book/${bookingId}/cancel`,
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