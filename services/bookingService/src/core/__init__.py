"""
Core package for shared functionality
"""

from .enums import BookingStatus

__all__ = ['BookingStatus']

# Re-export BookingStatus at the package level
BookingStatus = BookingStatus 