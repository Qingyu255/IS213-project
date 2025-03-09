import { BookingStatus } from "@/types/booking";

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

export async function getUserBookings(userId: string): Promise<Booking[]> {
  const response = await fetch(`${TICKET_SERVICE_URL}/api/v1/tickets/user/${userId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch user tickets');
  }
  return response.json();
}

export async function getBooking(bookingId: string): Promise<Booking> {
  const response = await fetch(`${TICKET_SERVICE_URL}/api/v1/bookings/${bookingId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch booking');
  }
  return response.json();
}

export async function updateBookingStatus(bookingId: string, action: 'confirm' | 'cancel' | 'refund'): Promise<Booking> {
  const response = await fetch(`${TICKET_SERVICE_URL}/api/v1/bookings/${bookingId}/${action}`, {
    method: 'PUT',
  });
  if (!response.ok) {
    throw new Error(`Failed to ${action} booking`);
  }
  return response.json();
} 