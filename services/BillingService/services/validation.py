from pydantic import BaseModel, Field, validator
from typing import Optional
import re

class PaymentRequest(BaseModel):
    amount: int = Field(..., gt=0, description="Amount in cents")
    currency: str = Field(..., min_length=3, max_length=3, description="Currency code (e.g., 'usd')")
    source: str = Field(..., description="Stripe payment source token")
    description: Optional[str] = Field(None, max_length=255, description="Payment description")
    
    @validator('currency')
    def currency_must_be_lowercase(cls, v):
        if v != v.lower():
            raise ValueError('Currency code must be lowercase')
        return v
    
    @validator('source')
    def validate_source(cls, v):
        if not v.startswith('tok_') and not v.startswith('card_'):
            raise ValueError('Invalid payment source format')
        return v

class RefundRequest(BaseModel):
    charge_id: str = Field(..., min_length=10, description="Stripe charge ID to refund")
    amount: Optional[int] = Field(None, gt=0, description="Amount to refund in cents (if partial refund)")
    reason: Optional[str] = Field(None, description="Reason for refund")
    
    @validator('charge_id')
    def validate_charge_id(cls, v):
        if not v.startswith('ch_'):
            raise ValueError('Invalid charge ID format')
        return v

class InvoiceRequest(BaseModel):
    customer_email: str = Field(..., description="Customer email address")
    amount: int = Field(..., gt=0, description="Amount in cents")
    currency: str = Field(..., min_length=3, max_length=3, description="Currency code (e.g., 'usd')")
    description: Optional[str] = Field(None, max_length=255, description="Invoice description")
    
    @validator('customer_email')
    def validate_email(cls, v):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('Invalid email format')
        return v
    
    @validator('currency')
    def currency_must_be_lowercase(cls, v):
        if v != v.lower():
            raise ValueError('Currency code must be lowercase')
        return v 