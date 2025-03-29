from pydantic import BaseModel, Field
from typing import Optional, Dict
from enum import Enum

class RefundRequest(BaseModel):
    payment_intent_id: str = Field(..., description="Unique identifier for the payment intent to refund")
    amount: int = Field(..., description="Refund amount in cents")
    reason: Optional[str] = Field(None, description="Reason for the refund (optional)")
    metadata: Optional[Dict[str, str]] = Field(default_factory=dict, description="Additional metadata for the refund (optional)")

class RefundStatus(str, Enum):
    APPROVED = "APPROVED"
    FAILED = "FAILED"

class RefundResponse(BaseModel):
    status: RefundStatus
    message: str