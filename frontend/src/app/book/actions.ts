'use server';

import { stripe } from '@/lib/stripe';
import { BACKEND_ROUTES } from "@/constants/backend-routes";
import Stripe from 'stripe';

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
    payment_intent?: {
      id: string;
      status: string;
    } | null;
  };
  error?: string;
}

export async function createBooking(eventId: string, userId: string, bearerToken: string) {
  try {
    if (!bearerToken) {
      throw new Error("No authentication token found");
    }

    const response = await fetch(`${BACKEND_ROUTES.bookingService}/api/v1/bookings`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": bearerToken
      },
      body: JSON.stringify({
        eventId,
        userId,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to create booking");
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error creating booking:", error);
    throw error;
  }
}

export async function confirmBooking(bookingId: string, sessionId: string, bearerToken: string): Promise<{ success: boolean; error?: string; requiresAuth?: boolean }> {
  try {
    // Get the session details to get the payment intent ID
    const sessionResponse = await getBookingCheckoutSession(sessionId);
    if (!sessionResponse.success || !sessionResponse.session) {
      throw new Error("Failed to get session details");
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_BOOKING_SERVICE_URL}/api/v1/bookings/${bookingId}/confirm?session_id=${sessionId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': bearerToken
      }
    });

    if (!response.ok) {
      if (response.status === 401) {
        return {
          success: false,
          error: "Please log in to confirm your booking",
          requiresAuth: true
        };
      }
      throw new Error(`Failed to confirm booking: ${response.statusText}`);
    }

    return { success: true };
  } catch (error) {
    console.error('Error confirming booking:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to confirm booking'
    };
  }
}

export async function getBookingCheckoutSession(sessionId: string): Promise<CheckoutSessionResponse> {
  try {
    if (!stripe) {
      return {
        success: false,
        error: 'Stripe is not initialized'
      };
    }
    
    const session = await stripe.checkout.sessions.retrieve(sessionId, {
      expand: ['line_items', 'payment_intent']
    });
    
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
      metadata: session.metadata,
      payment_intent: session.payment_intent && typeof session.payment_intent !== 'string' ? {
        id: session.payment_intent.id,
        status: session.payment_intent.status
      } : null
    };
    
    return {
      success: true,
      session: serializedSession
    };
  } catch (error) {
    console.error('Error retrieving checkout session:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to retrieve checkout session'
    };
  }
} 