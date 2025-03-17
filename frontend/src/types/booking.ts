export enum BookingStatus {
  PENDING = "PENDING",
  CONFIRMED = "CONFIRMED",
  CANCELED = "CANCELED",
  REFUNDED = "REFUNDED"
}

export type BookingStatusTransition = {
  [key in BookingStatus]: BookingStatus[];
};

export const BOOKING_STATUS_TRANSITIONS: BookingStatusTransition = {
  [BookingStatus.PENDING]: [BookingStatus.CONFIRMED, BookingStatus.CANCELED],
  [BookingStatus.CONFIRMED]: [BookingStatus.REFUNDED],
  [BookingStatus.CANCELED]: [],
  [BookingStatus.REFUNDED]: []
};

export function canTransitionTo(currentStatus: BookingStatus, newStatus: BookingStatus): boolean {
  return BOOKING_STATUS_TRANSITIONS[currentStatus].includes(newStatus);
} 