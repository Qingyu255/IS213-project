import { BookingStatus } from "@/types/booking";
import { fetchAuthSession } from "aws-amplify/auth";

const TICKET_SERVICE_URL = process.env.NEXT_PUBLIC_TICKET_SERVICE_URL || "http://localhost:8000";

export interface BookingRequest {
  event_id: string;
  num_tickets: number;
}

export interface BookingResponse {
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
  status: string;
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

export async function createBooking(bookingData: BookingRequest): Promise<BookingResponse> {
  const headers = await getAuthHeaders();
  const response = await fetch(`${TICKET_SERVICE_URL}/api/v1/bookings/book`, {
    method: 'POST',
    headers,
    body: JSON.stringify(bookingData)
  });
  if (!response.ok) {
    throw new Error('Failed to create booking');
  }
  return response.json();
}

export async function getUserBookings(userId: string): Promise<BookingResponse[]> {
  if (!isValidUUID(userId)) {
    throw new Error('Invalid user ID format. Must be a valid UUID.');
  }
  const headers = await getAuthHeaders();
  const response = await fetch(`${TICKET_SERVICE_URL}/api/v1/bookings/user/${userId}`, {
    headers
  });
  if (!response.ok) {
    throw new Error('Failed to fetch user bookings');
  }
  return response.json();
}

export async function getBooking(bookingId: string): Promise<BookingResponse> {
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

export async function updateBookingStatus(bookingId: string, action: 'confirm' | 'cancel' | 'refund'): Promise<{ message: string }> {
  if (!isValidUUID(bookingId)) {
    throw new Error('Invalid booking ID format. Must be a valid UUID.');
  }
  const headers = await getAuthHeaders();
  const response = await fetch(`${TICKET_SERVICE_URL}/api/v1/bookings/${bookingId}/${action}`, {
    method: 'POST',
    headers
  });
  if (!response.ok) {
    throw new Error(`Failed to ${action} booking`);
  }
  return response.json();
}

export async function getUserTickets(userId: string): Promise<Ticket[]> {
  if (!isValidUUID(userId)) {
    throw new Error('Invalid user ID format. Must be a valid UUID.');
  }
  const headers = await getAuthHeaders();
  const response = await fetch(`${TICKET_SERVICE_URL}/api/v1/tickets/user/${userId}`, {
    headers
  });
  if (!response.ok) {
    throw new Error('Failed to fetch user tickets');
  }
  return response.json();
}

export async function getEventTickets(eventId: string): Promise<Ticket[]> {
  if (!isValidUUID(eventId)) {
    throw new Error('Invalid event ID format. Must be a valid UUID.');
  }
  const headers = await getAuthHeaders();
  const response = await fetch(`${TICKET_SERVICE_URL}/api/v1/tickets/event/${eventId}`, {
    headers
  });
  if (!response.ok) {
    throw new Error('Failed to fetch event tickets');
  }
  return response.json();
}

export async function getAvailableTickets(eventId: string): Promise<{ available_tickets: number }> {
  if (!isValidUUID(eventId)) {
    throw new Error('Invalid event ID format. Must be a valid UUID.');
  }
  const headers = await getAuthHeaders();
  const response = await fetch(`${TICKET_SERVICE_URL}/api/v1/tickets/available/${eventId}`, {
    headers
  });
  if (!response.ok) {
    throw new Error('Failed to fetch available tickets');
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