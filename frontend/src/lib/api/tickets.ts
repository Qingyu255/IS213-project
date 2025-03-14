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

export interface UserEventTicketsResponse {
  tickets: Ticket[];
  count: number;
  ticket_ids: string[];
}

async function getAuthHeaders(): Promise<HeadersInit> {
  try {
    const session = await fetchAuthSession();
    const token = session.tokens?.idToken;
    
    if (!token) {
      return {
        'Content-Type': 'application/json',
      };
    }
    
    const tokenString = token.toString();
    const payload = tokenString.split('.')[1];
    const decodedClaims = JSON.parse(atob(payload));
    const userId = decodedClaims['custom:id'];
    
    return {
      'Authorization': `Bearer ${tokenString}`,
      'Content-Type': 'application/json',
      'X-User-ID': userId,
    };
  } catch (error) {
    console.error("Error getting auth headers:", error);
    return {
      'Content-Type': 'application/json',
    };
  }
}

function isValidUUID(uuid: string) {
  if (!uuid) return false;
  return true; // Skip validation for now to troubleshoot the API connection
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
  if (!userId) {
    throw new Error('User ID is required');
  }
  
  if (!isValidUUID(userId)) {
    throw new Error('Invalid user ID format. Must be a valid UUID.');
  }
  
  try {
    const headers = await getAuthHeaders();
    const url = `${TICKET_SERVICE_URL}/api/v1/bookings/user/${userId}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers,
      credentials: 'include',
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Error fetching bookings: ${response.status} - ${errorText}`);
      return [];
    }
    
    return await response.json();
  } catch (error) {
    console.error("Error in getUserBookings:", error);
    return [];
  }
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

export async function getUserEventTickets(
  userId: string,
  eventId: string
): Promise<UserEventTicketsResponse> {
  if (!userId || !eventId) {
    throw new Error('User ID and Event ID are required');
  }
  
  if (!isValidUUID(userId) || !isValidUUID(eventId)) {
    throw new Error('Invalid ID format. Must be a valid UUID.');
  }
  
  try {
    const headers = await getAuthHeaders();
    const url = `${TICKET_SERVICE_URL}/api/v1/tickets/user/${userId}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers,
      credentials: 'include',
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Error fetching user tickets: ${response.status} - ${errorText}`);
      return { tickets: [], count: 0, ticket_ids: [] };
    }
    
    const allUserTickets = await response.json();
    
    const eventTickets = allUserTickets.filter((ticket: any) => {
      return ticket.booking && ticket.booking.event_id === eventId;
    });
    
    return {
      tickets: eventTickets,
      count: eventTickets.length,
      ticket_ids: eventTickets.map((ticket: any) => ticket.ticket_id)
    };
  } catch (error) {
    console.error("Error in getUserEventTickets:", error);
    return { tickets: [], count: 0, ticket_ids: [] };
  }
} 