"""
Booking Payment model for storing payment data related to ticket bookings
"""
from sqlalchemy import Column, Integer, String, TIMESTAMP, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from . import Base

class BookingPayment(Base):
    """Model for storing booking payment data"""
    __tablename__ = 'booking_payments'
    
    id = Column(Integer, primary_key=True)
    booking_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    payment_intent_id = Column(String(255), nullable=False, index=True)
    amount = Column(BigInteger, nullable=False)
    currency = Column(String(10), nullable=False)
    status = Column(String(50), nullable=False, index=True)
    customer_email = Column(String(255))
    customer_name = Column(String(255))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<BookingPayment(booking_id='{self.booking_id}', payment_intent_id='{self.payment_intent_id}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'booking_id': str(self.booking_id),
            'payment_intent_id': self.payment_intent_id,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'customer_email': self.customer_email,
            'customer_name': self.customer_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 