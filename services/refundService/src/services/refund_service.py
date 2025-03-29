# src/services/refund_service.py
from fastapi import HTTPException
from src.clients.billing_client import BillingClient
from src.messaging.logging_publisher import (
    publish_refund_request_log,
    publish_refund_status_log
)
from src.models.refund_models import RefundRequest, RefundResponse, RefundStatus


class RefundService:
    def __init__(self):
        self.billing_client = BillingClient()
        
    def process_refund(self, refund_request: RefundRequest) -> RefundResponse:
        service_name = "refund_composite_service"
        
        # 1. Publish the refund request log.
        publish_refund_request_log(
            service_name=service_name,
            transaction_id=refund_request.payment_intent_id,
            message="Refund request initiated",
            level="INFO"
        )
        
        # 2. Call the Billing service's refund process endpoint.
        #    Assume the BillingClient's process_refund returns a dict with a "success" key.
        result = self.billing_client.process_refund(
            payment_intent_id=refund_request.payment_intent_id,
            amount=refund_request.amount,
            reason=refund_request.reason,
            metadata=refund_request.metadata
        )
        print(result)
        
        # 3. Log the refund status based on the response.
        if result.get("success"):
            publish_refund_status_log(
                service_name=service_name,
                transaction_id=refund_request.payment_intent_id,
                message="Refund processed successfully",
                is_error=False
            )
            return RefundResponse(
                status=RefundStatus.APPROVED,
                message="Refund processed successfully."
            )
        else:
            publish_refund_status_log(
                service_name=service_name,
                transaction_id=refund_request.payment_intent_id,
                message="Refund processing failed: " + result.get("message", "Unknown error"),
                is_error=True
            )
            # Raise an HTTPException with a 404 status code for any error.
            raise HTTPException(status_code=result.get("error_code", 404), detail=result.get("message", "Refund processing failed."))
