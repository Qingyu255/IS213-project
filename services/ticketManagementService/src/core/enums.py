from enum import Enum
import logging

logger = logging.getLogger(__name__)

class BookingStatus(str, Enum):
    PENDING = 'PENDING'
    CONFIRMED = 'CONFIRMED'
    CANCELED = 'CANCELED'
    REFUNDED = 'REFUNDED'

    @classmethod
    def can_transition_to(cls, current_status: str, new_status: str) -> bool:
        transitions = {
            cls.PENDING: [cls.CONFIRMED, cls.CANCELED],
            cls.CONFIRMED: [cls.REFUNDED, cls.CANCELED],
            cls.CANCELED: [],
            cls.REFUNDED: []
        }
        logger.debug(f"Checking transition from {current_status} to {new_status}")
        logger.debug(f"Available transitions: {transitions.get(current_status, [])}")
        
        current = current_status.upper() if isinstance(current_status, str) else current_status
        new = new_status.upper() if isinstance(new_status, str) else new_status
        
        return cls(new) in transitions.get(cls(current), [])