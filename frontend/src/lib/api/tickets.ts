import { BookingStatus } from "@/types/booking";
import { fetchAuthSession } from "aws-amplify/auth";

const TICKET_SERVICE_URL = process.env.NEXT_PUBLIC_TICKET_SERVICE_URL || "http://localhost:8000";

export interface Booking {
  booking_id: string;
  user_id: string;
  event_id: string;
  status: BookingStatus;
  created_at: string;
  updated_at: string;
  tickets: Ticket[];
}

export interface Ticket {
  ticket_id: string;
  booking_id: string;
}

// Helper function to get auth headers
async function getAuthHeaders(): Promise<HeadersInit> {
  const session = await fetchAuthSession();
  const token = session.tokens?.idToken || session.tokens?.accessToken;
  
  if (!token) {
    throw new Error('No authentication token available');
  }
  
  return {
    'Authorization': `Bearer ${token.toString()}`,
    'Content-Type': 'application/json',
  };
}

// Helper function to validate UUID format
function isValidUUID(uuid: string) {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
}

export async function getUserBookings(userId: string): Promise<Booking[]> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${TICKET_SERVICE_URL}/api/v1/bookings/user/${userId}`, {
    headers
  });
  if (!response.ok) {
    throw new Error('Failed to fetch user tickets');
  }
  return response.json();
}

export async function getBooking(bookingId: string): Promise<Booking> {
  if (!isValidUUID(bookingId)) {
    throw new Error('Invalid booking ID format. Must be a valid UUID.');
  }
  const headers = await getAuthHeaders();
  const response = await fetch(`${TICKET_SERVICE_URL}/api/v1/bookings/${bookingId}`, {
    headers
  });
  if (!response.ok) {
    throw new Error('Failed to fetch booking');
  }
  return response.json();
}

export async function updateBookingStatus(bookingId: string, action: 'confirm' | 'cancel' | 'refund'): Promise<Booking> {
  if (!isValidUUID(bookingId)) {
    throw new Error('Invalid booking ID format. Must be a valid UUID.');
  }
  const headers = await getAuthHeaders();
  const response = await fetch(`${TICKET_SERVICE_URL}/api/v1/bookings/${bookingId}/${action}`, {
    method: 'PUT',
    headers
  });
  if (!response.ok) {
    throw new Error(`Failed to ${action} booking`);
  }
  return response.json();
}

export async function testAuth(): Promise<any> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${TICKET_SERVICE_URL}/api/v1/bookings/test-auth`, {
    headers
  });
  if (!response.ok) {
    throw new Error('Authentication test failed');
  }
  return response.json();
} 