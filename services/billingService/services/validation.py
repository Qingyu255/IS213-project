from pydantic import BaseModel, Field, validator
from typing import Dict, Optional, Any
from decimal import Decimal

class PaymentRequest(BaseModel):
    """Validation model for payment request data"""
    event_id: str = Field(..., description="Event ID for the payment")
    amount: int = Field(..., gt=0, description="Amount in cents")
    currency: str = Field(..., description="3-letter currency code", pattern='^[a-z]{3}$')
    payment_method: Optional[str] = Field(None, description="Stripe Payment Method ID")
    description: Optional[str] = Field(None, description="Payment description")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata")
    customer_email: Optional[str] = Field(None, description="Customer email for receipt")

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v

    @validator('currency')
    def validate_currency(cls, v):
        if len(v) != 3:
            raise ValueError('Currency code must be 3 letters')
        return v.lower()

    @validator('event_id')
    def validate_event_id(cls, v):
        if not v:
            raise ValueError('Event ID is required')
        return v

class InvoiceRequest(BaseModel):
    """Validation model for invoice request data"""
    customer: str = Field(..., description="Stripe Customer ID")
    items: list = Field(..., description="List of invoice items")
    description: Optional[str] = Field(None, description="Invoice description")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata")
    auto_advance: bool = Field(True, description="Whether to auto-advance the invoice")
    collection_method: str = Field("charge_automatically", description="Collection method")
    days_until_due: Optional[int] = Field(None, description="Days until due for 'send_invoice' collection method")

    @validator('collection_method')
    def validate_collection_method(cls, v):
        if v not in ["charge_automatically", "send_invoice"]:
            raise ValueError('Invalid collection method')
        return v

class RefundRequest(BaseModel):
    """Validation model for refund request data"""
    payment_intent_id: str = Field(..., description="Stripe Payment Intent ID")
    amount: Optional[int] = Field(None, description="Amount to refund in cents")
    reason: Optional[str] = Field("requested_by_customer", description="Reason for refund")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata")

    @validator('payment_intent_id')
    def validate_payment_intent_id(cls, v):
        if not v.startswith('pi_'):
            raise ValueError('Invalid payment intent ID format')
        return v

    @validator('amount')
    def validate_amount(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Refund amount must be greater than 0')
        return v

def validate_stripe_id(id_str: str, prefix: str) -> bool:
    """Validate Stripe ID format (e.g., pi_, re_, ch_)"""
    return id_str.startswith(prefix)

def validate_amount(amount: int) -> bool:
    """Validate amount is positive"""
    return amount > 0 