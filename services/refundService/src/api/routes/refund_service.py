# src/api/routes/refund_service.py

from fastapi import APIRouter, HTTPException, Header
from src.models.refund_models import EventRefundRequest, EventRefundResponse, BookingRefundRequest , BookingRefundResponse
from src.services.refund_service import RefundService

router = APIRouter()
refund_service = RefundService()

@router.post("/event-refund", response_model=EventRefundResponse)
def process_refund(event_refund_request: EventRefundRequest):
    """
    Processes a refund request by invoking the refund service.
    
    - **refund_request**: A JSON body conforming to EventRefundRequest model.
      Requires 'event_id' and 'organizer_id'
    
    Returns a EventRefundResponse with the status and message
    """
    try:
        response = refund_service.process_refund(event_refund_request)
        return response
    except HTTPException as exc:
        # If RefundService raises an HTTPException (e.g. with 404), re-raise it directly
        raise exc
    except Exception as e:
        # For any other unexpected error, return a 500
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/booking-refund", response_model=BookingRefundResponse)
def process_booking_refund(booking_refund_request: BookingRefundRequest, authorization: str = Header(None, description="Bearer token for authentication")
):
    """
    Processes a booking refund request by invoking the refund service.
    
    - **booking_refund_request**: A JSON body conforming to BookingRefundRequest model.
      Requires 'booking_id'
    
    Returns a BookingRefundResponse with the status and message
    """
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header is missing")
        
        response = refund_service.process_booking_refund(booking_refund_request)
        return response
    except HTTPException as exc:
        # If RefundService raises an HTTPException (e.g., with 404), re-raise it directly
        raise exc
    except Exception as e:
        # For any other unexpected error, return a 500
        raise HTTPException(status_code=500, detail=str(e))