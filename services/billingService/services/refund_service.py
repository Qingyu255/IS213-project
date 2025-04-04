import logging
import stripe
from services.validation import RefundRequest, validate_stripe_id
from typing import Dict, Tuple, Optional, Any
from config import Config

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)

class RefundService:
    @staticmethod
    def process_refund(refund_data: dict) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Process a refund for a payment.
        Ensures the payment is completed and chargeable before processing refund.
        
        Args:
            refund_data (dict): Validated refund data from RefundRequest model
                
        Returns:
            tuple: (refund_details, error_str)
        """
        try:
            logger.info(f"Processing refund with data: {refund_data}")
            
            # Get the payment intent first
            try:
                payment_intent = stripe.PaymentIntent.retrieve(refund_data['payment_intent_id'])
                logger.info(f"Retrieved payment intent: {payment_intent.id}")
                logger.info(f"Payment intent status: {payment_intent.status}")
                
                # Verify payment has succeeded
                if payment_intent.status != 'succeeded':
                    logger.warning(f"Payment {payment_intent.id} has not succeeded. Current status: {payment_intent.status}")
                    return None, f"Cannot refund payment that has not succeeded. Current status: {payment_intent.status}"
                
                # Verify charge exists and has 
                charge_id = payment_intent.latest_charge
                if not charge_id:
                    logger.warning(f"No charges found for payment intent: {payment_intent.id}")
                    return None, "No charges found for this payment"
                logger.info(f"Found charge ID: {charge_id}")
                
                charge = stripe.Charge.retrieve(charge_id)
                if charge.status != 'succeeded':
                    logger.warning(f"Charge {charge_id} has not succeeded. Current status: {charge.status}")
                    return None, f"Cannot refund charge that has not succeeded. Current status: {charge.status}"
                
                # Check if charge is already refunded
                if charge.refunded:
                    logger.warning(f"Charge {charge_id} has already been refunded")
                    return None, "This charge has already been refunded"
                
                # charge_id = charge.id
                # logger.info(f"Charge ID retrieved: {charge_id}")
                
                # Prepare refund parameters
                refund_params = {
                    'charge': charge_id,
                    'reason': refund_data.get('reason', 'requested_by_customer'),
                    'metadata': refund_data.get('metadata', {})
                }
                
                # Add amount if specified and validate against charge amount
                if 'amount' in refund_data and refund_data['amount'] is not None:
                    refund_amount = refund_data['amount']
                    if refund_amount > charge.amount:
                        logger.warning(f"Refund amount {refund_amount} exceeds charge amount {charge.amount_captured}")
                        return None, "Refund amount cannot exceed the original charge amount"
                    refund_params['amount'] = refund_amount 
                
                logger.info(f"Creating refund with parameters: {refund_params}")
                
                # Create the refund
                refund = stripe.Refund.create(**refund_params)
                logger.info(f"Successfully created refund: {refund.id}")
                
                return {
                    'success': True,
                    'refund_id': refund.id,
                    'payment_intent_id': payment_intent.id,
                    'charge_id': charge_id,
                    'amount': refund.amount,
                    'currency': refund.currency,
                    'status': refund.status,
                    'reason': refund.reason,
                    'created': refund.created,
                    'metadata': refund.metadata,
                    'receipt_url': refund.receipt_url if hasattr(refund, 'receipt_url') else None
                }, None
                
            except stripe.error.InvalidRequestError as e:
                logger.warning(f"Payment intent not found: {str(e)}")
                return None, "Payment not found"
            
        except stripe.error.AuthenticationError as e:
            logger.critical(f"Stripe authentication failed: {str(e)}")
            return None, "Payment service authentication error"
        except stripe.error.APIConnectionError as e:
            logger.error(f"Could not connect to Stripe: {str(e)}")
            return None, "Payment service connection error"
        except stripe.error.InvalidRequestError as e:
            logger.error(f"Invalid refund request: {str(e)}")
            return None, f"Invalid refund request: {str(e)}"
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return None, f"Payment service error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in process_refund: {str(e)}", exc_info=True)
            return None, f"An unexpected error occurred while processing refund: {str(e)}"

    @staticmethod
    def get_refund(refund_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Get refund details by ID.
        
        Args:
            refund_id: Stripe Refund ID (re_...)
            
        Returns:
            tuple: (refund_details, error_str)
        """
        try:
            logger.info(f"Retrieving refund details for refund_id: {refund_id}")
            
            refund = stripe.Refund.retrieve(refund_id)
            logger.info(f"Successfully retrieved refund: {refund.id}")
            
            return {
                'refund_id': refund.id,
                'charge_id': refund.charge,
                'payment_intent_id': refund.payment_intent,
                'amount': refund.amount,
                'currency': refund.currency,
                'status': refund.status,
                'reason': refund.reason,
                'created': refund.created,
                'metadata': refund.metadata,
                'receipt_url': refund.receipt_url if hasattr(refund, 'receipt_url') else None
            }, None
            
        except stripe.error.InvalidRequestError as e:
            logger.warning(f"Refund not found: {str(e)}")
            return None, "Refund not found"
        except stripe.error.AuthenticationError as e:
            logger.critical(f"Stripe authentication failed: {str(e)}")
            return None, "Payment service authentication error"
        except stripe.error.APIConnectionError as e:
            logger.error(f"Could not connect to Stripe: {str(e)}")
            return None, "Payment service connection error"
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return None, f"Payment service error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in get_refund: {str(e)}", exc_info=True)
            return None, "An unexpected error occurred while retrieving refund details"

    @staticmethod
    def verify_refund(refund_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Verify the status of a refund.
        Ensures the refund has been processed successfully.
        
        Args:
            refund_id: Stripe Refund ID (re_...)
            
        Returns:
            tuple: (verification_details, error_str)
        """
        try:
            logger.info(f"Verifying refund for refund_id: {refund_id}")
            
            refund = stripe.Refund.retrieve(refund_id)
            logger.info(f"Successfully retrieved refund for verification: {refund.id}")
            
            # Verify refund status
            if refund.status != 'succeeded':
                logger.warning(f"Refund {refund.id} has not succeeded. Current status: {refund.status}")
                return None, f"Refund has not succeeded. Current status: {refund.status}"
            
            # Get the associated charge
            charge = stripe.Charge.retrieve(refund.charge)
            logger.info(f"Retrieved associated charge: {charge.id}")
            
            verification = {
                'refund_id': refund.id,
                'verified': True,
                'status': refund.status,
                'is_succeeded': True,
                'amount': refund.amount,
                'currency': refund.currency,
                'charge_id': refund.charge,
                'payment_intent_id': refund.payment_intent,
                'reason': refund.reason,
                'created': refund.created,
                'receipt_url': refund.receipt_url if hasattr(refund, 'receipt_url') else None,
                'charge_status': charge.status,
                'charge_amount': charge.amount,
                'charge_refunded': charge.refunded,
                'charge_dispute': charge.dispute is not None
            }
            
            logger.info(f"Refund {refund.id} verified successfully")
            return verification, None
            
        except stripe.error.InvalidRequestError as e:
            logger.warning(f"Refund not found: {str(e)}")
            return None, "Refund not found"
        except stripe.error.AuthenticationError as e:
            logger.critical(f"Stripe authentication failed: {str(e)}")
            return None, "Payment service authentication error"
        except stripe.error.APIConnectionError as e:
            logger.error(f"Could not connect to Stripe: {str(e)}")
            return None, "Payment service connection error"
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return None, f"Payment service error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in verify_refund: {str(e)}", exc_info=True)
            return None, "An unexpected error occurred while verifying refund" 