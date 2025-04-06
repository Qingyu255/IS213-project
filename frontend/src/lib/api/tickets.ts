/* eslint-disable @typescript-eslint/no-explicit-any */
import { BookingStatus } from "@/types/booking";
import { fetchAuthSession } from "aws-amplify/auth";
import { getBearerIdToken, getBearerToken } from "@/utils/auth"

const TICKET_SERVICE_URL = typeof window === 'undefined' 
  ? process.env.TICKET_SERVICE_URL  // Use container name when running in Docker
  : 'http://localhost:8000';        // Use localhost when running in browser

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
  total_amount: number;
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
        "Content-Type": "application/json",
      };
    }

    const tokenString = token.toString();
    const payload = tokenString.split(".")[1];
    const decodedClaims = JSON.parse(atob(payload));
    const userId = decodedClaims["custom:id"];

    return {
      Authorization: `Bearer ${tokenString}`,
      "Content-Type": "application/json",
      "X-User-ID": userId,
    };
  } catch (error) {
    console.error("Error getting auth headers:", error);
    return {
      "Content-Type": "application/json",
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
    method: "POST",
    headers,
    body: JSON.stringify(bookingData),
  });

  if (!response.ok) {
    throw new Error("Failed to create booking");
  }

  const booking = await response.json();
  return booking;  // Backend will auto-confirm if free event
}

export async function getUserBookings(
  userId: string
): Promise<BookingResponse[]> {
  if (!userId) {
    throw new Error("User ID is required");
  }

  if (!isValidUUID(userId)) {
    throw new Error("Invalid user ID format. Must be a valid UUID.");
  }

  try {
    const headers = await getAuthHeaders();
    const url = `${TICKET_SERVICE_URL}/api/v1/bookings/user/${userId}`;

    const response = await fetch(url, {
      method: "GET",
      headers,
      credentials: "include",
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(
        `Error fetching bookings: ${response.status} - ${errorText}`
      );
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
    throw new Error("Invalid booking ID format. Must be a valid UUID.");
  }
  
  const headers = await getAuthHeaders();
  console.log("Fetching booking with ID:", bookingId); // Debug log
  
  const response = await fetch(
    `${TICKET_SERVICE_URL}/api/v1/bookings/${bookingId}`,
    {
      headers,
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    console.error("Error fetching booking:", {
      status: response.status,
      error: errorData
    });
    throw new Error(
      errorData?.detail || 
      `Failed to fetch booking (${response.status})`
    );
  }

  const data = await response.json();
  console.log("Booking data received:", data); // Debug log
  return data;
}

export async function updateBookingStatus(
  bookingId: string,
  action: "cancel" | "refund" | "complete"
): Promise<{ message: string }> {
  const endpoint = action === "complete" ? "confirm" : action;
  const headers = await getAuthHeaders();
  
  console.log('Making request to:', `${TICKET_SERVICE_URL}/api/v1/bookings/${bookingId}/${endpoint}`);
  
  try {
    const response = await fetch(
      `${TICKET_SERVICE_URL}/api/v1/bookings/${bookingId}/${endpoint}`,
      {
        method: "POST",
        headers,
        credentials: 'include',
      }
    );

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.detail || `Failed to ${action} booking`);
    }
    
    return data;
  } catch (error) {
    console.error('Error updating booking status:', error);
    throw error;
  }
}

export async function getUserTickets(userId: string): Promise<Ticket[]> {
  if (!isValidUUID(userId)) {
    throw new Error("Invalid user ID format. Must be a valid UUID.");
  }
  const headers = await getAuthHeaders();
  const response = await fetch(
    `${TICKET_SERVICE_URL}/api/v1/tickets/user/${userId}`,
    {
      headers,
    }
  );
  if (!response.ok) {
    throw new Error("Failed to fetch user tickets");
  }
  return response.json();
}

export async function getEventTickets(eventId: string): Promise<Ticket[]> {
  if (!isValidUUID(eventId)) {
    throw new Error("Invalid event ID format. Must be a valid UUID.");
  }
  const headers = await getAuthHeaders();
  const response = await fetch(
    `${TICKET_SERVICE_URL}/api/v1/tickets/event/${eventId}`,
    {
      headers,
    }
  );
  if (!response.ok) {
    throw new Error("Failed to fetch event tickets");
  }
  return response.json();
}

export async function getAvailableTickets(eventId: string) {
  try {
    const headers = await getAuthHeaders()
    // Check if headers is missing Authorization
    if (!(headers as Record<string, string>)['Authorization']) {
      return { available_tickets: null }
    }

    const response = await fetch(
      `${TICKET_SERVICE_URL}/api/v1/tickets/event/${eventId}/available`,
      { headers }
    )

    if (!response.ok) {
      return { available_tickets: null }
    }

    return await response.json()
  } catch (error) {
    console.error("Error fetching tickets:", error)
    return { available_tickets: null }
  }
}

export async function testAuth(): Promise<any> {
  const headers = await getAuthHeaders();
  const response = await fetch(
    `${TICKET_SERVICE_URL}/api/v1/bookings/test-auth`,
    {
      headers,
    }
  );
  if (!response.ok) {
    throw new Error("Authentication test failed");
  }
  return response.json();
}

export async function getUserEventTickets(
  userId: string,
  eventId: string
): Promise<UserEventTicketsResponse> {
  if (!userId || !eventId) {
    throw new Error("User ID and Event ID are required");
  }

  if (!isValidUUID(userId) || !isValidUUID(eventId)) {
    throw new Error("Invalid ID format. Must be a valid UUID.");
  }

  try {
    const headers = await getAuthHeaders();
    const url = `${TICKET_SERVICE_URL}/api/v1/tickets/user/${userId}`;

    const response = await fetch(url, {
      method: "GET",
      headers,
      credentials: "include",
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(
        `Error fetching user tickets: ${response.status} - ${errorText}`
      );
      return { tickets: [], count: 0, ticket_ids: [] };
    }

    const allUserTickets = await response.json();

    const eventTickets = allUserTickets.filter((ticket: any) => {
      return ticket.booking && ticket.booking.event_id === eventId;
    });

    return {
      tickets: eventTickets,
      count: eventTickets.length,
      ticket_ids: eventTickets.map((ticket: any) => ticket.ticket_id),
    };
  } catch (error) {
    console.error("Error in getUserEventTickets:", error);
    return { tickets: [], count: 0, ticket_ids: [] };
  }
}
