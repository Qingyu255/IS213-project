from enum import Enum

class BookingStatus(str, Enum):
    PENDING = 'PENDING'
    CONFIRMED = 'CONFIRMED'
    CANCELED = 'CANCELED'
    REFUNDED = 'REFUNDED'

    @classmethod
    def can_transition_to(cls, current_status: str, new_status: str) -> bool:
        transitions = {
            cls.PENDING: [cls.CONFIRMED, cls.CANCELED],
            cls.CONFIRMED: [cls.REFUNDED],
            cls.CANCELED: [],
            cls.REFUNDED: []
        }
        return new_status in transitions.get(current_status, [])