# src/api/routes/refund_service.py

from fastapi import APIRouter, HTTPException
from src.models.refund_models import RefundRequest, RefundResponse
from src.services.refund_service import RefundService

router = APIRouter()
refund_service = RefundService()

@router.post("/refund", response_model=RefundResponse)
def process_refund(refund_request: RefundRequest):
    """
    Processes a refund request by invoking the refund service.
    
    - **refund_request**: A JSON body conforming to RefundRequest model.
    
    Returns a RefundResponse with the status and message
    """
    try:
        response = refund_service.process_refund(refund_request)
        return response
    except HTTPException as exc:
        # If RefundService raises an HTTPException (e.g. with 404), re-raise it directly
        raise exc
    except Exception as e:
        # For any other unexpected error, return a 500
        raise HTTPException(status_code=500, detail=str(e))
