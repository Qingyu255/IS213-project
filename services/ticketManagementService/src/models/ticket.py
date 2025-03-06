from sqlalchemy import Column, String, UUID, DateTime, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    booking_id = Column(UUID, ForeignKey("bookings.booking_id", ondelete="CASCADE"), nullable=False)
