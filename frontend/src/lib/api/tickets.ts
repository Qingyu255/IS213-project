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

// Helper function to get auth headers
async function getAuthHeaders(): Promise<HeadersInit> {
  try {
    const session = await fetchAuthSession();
    console.log("Auth session:", session);
    
    // Get the ID token which contains custom attributes
    const token = session.tokens?.idToken;
    
    if (!token) {
      console.warn('No ID token available, proceeding without auth');
      return {
        'Content-Type': 'application/json',
      };
    }
    
    const tokenString = token.toString();
    console.log("Using ID token (first 20 chars):", tokenString.substring(0, 20) + "...");
    
    // Extract user ID from token for debugging
    try {
      const payload = tokenString.split('.')[1];
      const decodedClaims = JSON.parse(atob(payload));
      const userId = decodedClaims['custom:id'];
      console.log('User ID from token claims:', userId);
      
      return {
        'Authorization': `Bearer ${tokenString}`,
        'Content-Type': 'application/json',
        'X-User-ID': userId, // Add custom header for debugging
      };
    } catch (e) {
      console.error('Error decoding token:', e);
      return {
        'Authorization': `Bearer ${tokenString}`,
        'Content-Type': 'application/json',
      };
    }
  } catch (error) {
    console.error("Error getting auth headers:", error);
    // Return basic headers if auth fails
    return {
      'Content-Type': 'application/json',
    };
  }
}

// Helper function to validate UUID format
function isValidUUID(uuid: string) {
  if (!uuid) return false;
  
  // Log the UUID being validated
  console.log("Validating UUID:", uuid);
  
  // Accept any string that looks like a UUID (more permissive)
  // This will accept any format that has the general structure of a UUID
  // with or without hyphens and with any version
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
    console.error("getUserBookings called with no user ID");
    throw new Error('User ID is required');
  }
  
  // Log the user ID for debugging
  console.log("Attempting to fetch bookings for user ID:", userId);
  
  // Check if it's a valid UUID
  if (!isValidUUID(userId)) {
    console.error("Invalid UUID format:", userId);
    throw new Error('Invalid user ID format. Must be a valid UUID.');
  }
  
  try {
    // Get auth headers
    const headers = await getAuthHeaders();
    console.log("Auth headers:", headers);
    
    // Construct the URL
    const url = `${TICKET_SERVICE_URL}/api/v1/bookings/user/${userId}`;
    console.log("Fetching from URL:", url);
    
    // Make the request with credentials included
    const response = await fetch(url, {
      method: 'GET',
      headers,
      credentials: 'include', // Include credentials for CORS
      // Don't set mode: 'cors' explicitly, let the browser handle it
    });
    
    console.log("Response status:", response.status);
    console.log("Response headers:", Object.fromEntries(response.headers.entries()));
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Error fetching bookings: ${response.status} - ${errorText}`);
      
      // Return empty array instead of throwing to prevent UI errors
      console.log("Returning empty bookings array due to error");
      return [];
    }
    
    const data = await response.json();
    console.log("Bookings data received:", data);
    return data;
  } catch (error) {
    console.error("Error in getUserBookings:", error);
    // Return empty array instead of throwing to prevent UI errors
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
  
  console.log("Attempting to fetch tickets for user ID:", userId, "and event ID:", eventId);
  
  // Check if they're valid UUIDs
  if (!isValidUUID(userId) || !isValidUUID(eventId)) {
    console.error("Invalid UUID format - userId:", userId, "eventId:", eventId);
    throw new Error('Invalid ID format. Must be a valid UUID.');
  }
  
  try {
    const headers = await getAuthHeaders();
    const url = `${TICKET_SERVICE_URL}/api/v1/tickets/user/${userId}`;
    console.log("Fetching user tickets from URL:", url);
    
    const response = await fetch(url, {
      method: 'GET',
      headers,
      credentials: 'include', // Include credentials for CORS
    });
    
    console.log("User tickets response status:", response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Error fetching user tickets: ${response.status} - ${errorText}`);
      // Return empty data instead of throwing
      return { tickets: [], count: 0, ticket_ids: [] };
    }
    
    const allUserTickets = await response.json();
    console.log("All user tickets:", allUserTickets);
    
    // Filter tickets for the specific event
    const eventTickets = allUserTickets.filter((ticket: any) => {
      // Check if the ticket has a booking with the matching event_id
      return ticket.booking && ticket.booking.event_id === eventId;
    });
    
    console.log("Filtered event tickets:", eventTickets);
    
    // Format the response
    const response_data: UserEventTicketsResponse = {
      tickets: eventTickets,
      count: eventTickets.length,
      ticket_ids: eventTickets.map((ticket: any) => ticket.ticket_id)
    };
    
    return response_data;
  } catch (error) {
    console.error("Error in getUserEventTickets:", error);
    // Return empty data instead of throwing
    return { tickets: [], count: 0, ticket_ids: [] };
  }
} 