from enum import Enum

class BookingStatus(str, Enum):
    PENDING = 'PENDING'
    CONFIRMED = 'CONFIRMED'
    CANCELED = 'CANCELED'
    REFUNDED = 'REFUNDED'