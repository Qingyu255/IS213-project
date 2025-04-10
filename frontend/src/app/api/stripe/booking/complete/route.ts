import { NextResponse } from 'next/server';
import { stripe } from '@/lib/stripe';
import { BACKEND_ROUTES } from '@/constants/backend-routes';

// Use internal Docker network URLs when running on server-side
const TICKET_SERVICE_URL = 'http://ticket-management-service:8000';
const EVENT_SERVICE_URL = 'http://event-service:8000';

export async function POST(request: Request) {
  try {
    if (!stripe) {
      throw new Error('Stripe is not initialized');
    }

    // Check for authorization header
    const authHeader = request.headers.get('authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      );
    }

    // Get the request data
    const data = await request.json();
    const { bookingId } = data;

    if (!bookingId) {
      return NextResponse.json(
        { error: 'Missing required parameters' },
        { status: 400 }
      );
    }

    try {
      console.log('Fetching booking details for ID:', bookingId);
      
      // Get booking details by directly calling the ticket service
      const response = await fetch(
        `${TICKET_SERVICE_URL}/api/v1/mgmt/bookings/${bookingId}`,
        {
          headers: {
            Authorization: authHeader,
            "Content-Type": "application/json"
          }
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        if (response.status === 401) {
          return NextResponse.json(
            { error: 'Could not validate credentials' },
            { status: 401 }
          );
        }
        throw new Error(errorData?.detail || `Failed to fetch booking (${response.status})`);
      }

      const booking = await response.json();
      console.log('Booking response:', booking);
      
      if (!booking) {
        return NextResponse.json(
          { error: 'Booking not found' },
          { status: 404 }
        );
      }

      if (booking.status !== 'PENDING') {
        return NextResponse.json(
          { error: 'This booking is not in a pending state' },
          { status: 400 }
        );
      }

      // Fetch event details to get the price
      const eventResponse = await fetch(
        `${EVENT_SERVICE_URL}/api/v1/events/${booking.event_id}`,
        {
          headers: {
            Authorization: authHeader,
            "Content-Type": "application/json"
          }
        }
      );

      if (!eventResponse.ok) {
        throw new Error('Failed to fetch event details');
      }

      const eventDetails = await eventResponse.json();
      console.log('Event details:', eventDetails);

      // Calculate total amount (price in cents * number of tickets)
      const priceInCents = Math.round(eventDetails.price * 100); // Convert to cents
      const ticketCount = booking.tickets?.length || 1;
      const totalAmount = priceInCents * ticketCount;

      console.log('Price in cents:', priceInCents);
      console.log('Ticket count:', ticketCount);
      console.log('Calculated total amount:', totalAmount);

      // Determine the origin for success and cancel URLs
      const origin = request.headers.get('origin') || 'http://localhost:3000';

      const eventTitle = eventDetails.title || 'Event Ticket';

      // Create a checkout session
      const session = await stripe.checkout.sessions.create({
        payment_method_types: ['card'],
        line_items: [
          {
            price_data: {
              currency: 'sgd',
              product_data: {
                name: eventTitle,
                description: `Booking for ${ticketCount} ticket${ticketCount > 1 ? 's' : ''}`,
              },
              unit_amount: priceInCents, // Use price per ticket
            },
            quantity: ticketCount, // Set quantity instead of multiplying price
          },
        ],
        metadata: {
          booking_id: bookingId,
        },
        mode: 'payment',
        success_url: `${origin}/book/${bookingId}/success?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${origin}/my-events`,
      });

      if (!session.url) {
        throw new Error('Failed to create checkout session URL');
      }

      return NextResponse.json({ url: session.url });
    } catch (error) {
      console.error('Error processing booking:', error);
      if (error instanceof Error && error.message === 'Could not validate credentials') {
        return NextResponse.json(
          { error: 'Could not validate credentials' },
          { status: 401 }
        );
      }
      return NextResponse.json(
        { error: error instanceof Error ? error.message : 'Failed to process booking' },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Error creating checkout session:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'An unknown error occurred' },
      { status: 500 }
    );
  }
} 