"""
Payment Verification model for storing Stripe webhook events
"""
from sqlalchemy import Column, Integer, String, TIMESTAMP, BigInteger, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from . import Base

class PaymentVerification(Base):
    """
    Model for storing payment verification data from Stripe webhooks
    """
    __tablename__ = 'payment_verifications'
    
    id = Column(Integer, primary_key=True)
    payment_id = Column(String(255), nullable=False, index=True)
    event_id = Column(String(255), index=True)
    user_id = Column(String(255), index=True)
    event_type = Column(String(100), nullable=False, index=True)
    amount = Column(BigInteger)
    currency = Column(String(10))
    status = Column(String(50))
    payment_method = Column(String(100))
    receipt_email = Column(String(255))
    receipt_url = Column(String(512))
    verification_data = Column(JSONB, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    recorded_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<PaymentVerification(id={self.id}, payment_id='{self.payment_id}', event_type='{self.event_type}')>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'payment_id': self.payment_id,
            'event_id': self.event_id,
            'user_id': self.user_id,
            'event_type': self.event_type,
            'amount': self.amount,
            'currency': self.currency,
            'status': self.status,
            'payment_method': self.payment_method,
            'receipt_email': self.receipt_email,
            'receipt_url': self.receipt_url,
            'verification_data': self.verification_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None
        } 