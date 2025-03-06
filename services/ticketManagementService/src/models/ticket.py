from sqlalchemy import Column, String, UUID, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(UUID, primary_key=True, server_default=func.gen_random_uuid())
    event_id = Column(UUID, nullable=False)
    user_id = Column(UUID, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
