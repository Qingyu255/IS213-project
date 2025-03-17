import logging
import stripe
from services.validation import RefundRequest
from typing import Dict, Tuple, Optional, Any
from config import Config

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)

class RefundService:
    @staticmethod
    def process_refund(data: dict, idempotency_key: Optional[str] = None) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Process a refund using Stripe's Payment Intents API.
        
        Args:
            data (dict):
                - payment_intent_id: Stripe PaymentIntent ID (pi_...)
                - amount: Optional amount in cents for partial refund
                - reason: Optional reason for refund
                - metadata: Optional additional metadata
            idempotency_key: Unique key to prevent duplicate refunds
            
        Returns:
            tuple: (refund_details, error_str)
                refund_details contains refund information if successful
        """
        try:
            if 'payment_intent_id' not in data:
                return None, "Missing payment_intent_id parameter"

            # Get the payment intent and validate it
            try:
                payment_intent = stripe.PaymentIntent.retrieve(data['payment_intent_id'])
            except stripe.error.InvalidRequestError:
                return None, "Invalid payment intent ID"

            if payment_intent.status != 'succeeded':
                return None, f"Payment intent status is {payment_intent.status}, must be succeeded to refund"

            if not payment_intent.charges.data:
                return None, "No charges found for this payment intent"

            charge = payment_intent.charges.data[0]
            
            # Validate refund amount
            if 'amount' in data:
                if data['amount'] <= 0:
                    return None, "Refund amount must be positive"
                if data['amount'] > charge.amount:
                    return None, f"Refund amount {data['amount']} exceeds charge amount {charge.amount}"

            # Check if already refunded
            if charge.refunded:
                return None, "Payment has already been fully refunded"
            if charge.amount_refunded + (data.get('amount', charge.amount)) > charge.amount:
                return None, f"Refund amount would exceed remaining refundable amount: {charge.amount - charge.amount_refunded}"

            # Prepare refund data
            refund_data = {
                'charge': charge.id,
                'reason': data.get('reason', 'requested_by_customer'),
                'metadata': data.get('metadata', {})
            }

            if 'amount' in data:
                refund_data['amount'] = data['amount']

            # Add idempotency key if provided
            if idempotency_key:
                refund_data['idempotency_key'] = idempotency_key

            # Process the refund
            try:
                refund = stripe.Refund.create(**refund_data)
            except stripe.error.InvalidRequestError as e:
                logger.error(f"Invalid refund request: {str(e)}")
                return None, str(e)

            return {
                "success": True,
                "refund_id": refund.id,
                "payment_intent_id": payment_intent.id,
                "charge_id": refund.charge,
                "amount": refund.amount,
                "currency": refund.currency,
                "status": refund.status,
                "reason": refund.reason,
                "created": refund.created,
                "metadata": refund.metadata,
                "remaining_refundable": charge.amount - (charge.amount_refunded + refund.amount)
            }, None

        except stripe.error.PermissionError:
            logger.error("Permission denied for refund operation")
            return None, "Permission denied for refund operation"
        except stripe.error.AuthenticationError:
            logger.critical("Stripe authentication failed")
            return None, "Refund service configuration error"
        except stripe.error.APIConnectionError:
            logger.error("Could not connect to Stripe")
            return None, "Refund service temporarily unavailable"
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return None, "Refund processing error"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None, "An unexpected error occurred"

    @staticmethod
    def get_refund(refund_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Get refund details by ID.
        Retrieves comprehensive information about a specific refund.
        
        Args:
            refund_id: Stripe Refund ID (re_...)
            
        Returns:
            tuple: (refund_details, error_str)
                refund_details contains full refund information and status
        """
        try:
            refund = stripe.Refund.retrieve(refund_id)
            
            # Get associated charge for additional details
            try:
                charge = stripe.Charge.retrieve(refund.charge)
            except stripe.error.InvalidRequestError:
                charge = None

            response = {
                "refund_id": refund.id,
                "charge_id": refund.charge,
                "payment_intent_id": refund.payment_intent,
                "amount": refund.amount,
                "currency": refund.currency,
                "status": refund.status,
                "reason": refund.reason,
                "created": refund.created,
                "metadata": refund.metadata,
                "failure_reason": refund.failure_reason,
                "failure_balance_transaction": refund.failure_balance_transaction,
                "receipt_url": refund.receipt_url if hasattr(refund, 'receipt_url') else None
            }

            if charge:
                response.update({
                    "charge_amount": charge.amount,
                    "amount_refunded_total": charge.amount_refunded,
                    "remaining_refundable": charge.amount - charge.amount_refunded,
                    "is_fully_refunded": charge.refunded
                })
            
            return response, None
            
        except stripe.error.InvalidRequestError as e:
            logger.warning(f"Invalid refund ID: {str(e)}")
            return None, "Refund not found"
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return None, "Error retrieving refund"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None, "An unexpected error occurred"

    @staticmethod
    def verify_refund(refund_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Verify the status of a refund.
        Similar to get_refund but focused on verification-specific details.
        
        Args:
            refund_id: Stripe Refund ID (re_...)
            
        Returns:
            tuple: (verification_details, error_str)
                verification_details includes refund status and processing info
        """
        try:
            refund = stripe.Refund.retrieve(refund_id)
            
            verification = {
                "refund_id": refund.id,
                "verified": True,
                "status": refund.status,
                "is_succeeded": refund.status == 'succeeded',
                "amount": refund.amount,
                "currency": refund.currency,
                "charge_id": refund.charge,
                "payment_intent_id": refund.payment_intent,
                "reason": refund.reason,
                "created": refund.created,
                "failure_reason": refund.failure_reason,
                "failure_balance_transaction": refund.failure_balance_transaction,
                "processing_status": {
                    "is_pending": refund.status == 'pending',
                    "is_failed": refund.status == 'failed',
                    "needs_action": False  # Refunds don't typically need additional action
                }
            }
            
            return verification, None
            
        except stripe.error.InvalidRequestError as e:
            logger.warning(f"Invalid refund ID: {str(e)}")
            return None, "Refund not found"
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return None, "Error verifying refund"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None, "An unexpected error occurred" 