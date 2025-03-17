import logging
import stripe
from services.validation import PaymentRequest, InvoiceRequest
from config import Config
from typing import Dict, Tuple, Optional, Any
from decimal import Decimal

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)

class PaymentService:
    SUPPORTED_CURRENCIES = {'sgd'}  # Only support SGD for now
    MINIMUM_AMOUNTS = {
        'sgd': 50   # S$0.50 minimum
    }

    @staticmethod
    def process_payment(payment_data: dict, idempotency_key: Optional[str] = None) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Create and process a payment using Stripe's Payment Intents API.
        Supports 3D Secure/SCA and handles asynchronous payment methods.
        
        Args:
            payment_data (dict):
                - amount: Amount in smallest currency unit (cents)
                - currency: Must be 'sgd'
                - payment_method: Stripe Payment Method ID
                - description: Optional payment description
                - metadata: Optional dict of metadata
                - customer_email: Optional customer email for receipt
            idempotency_key: Unique key to prevent duplicate payments
        
        Returns:
            tuple: (payment_details, error_str)
                payment_details contains:
                    - payment_intent_id: Stripe PaymentIntent ID
                    - client_secret: Required for 3DS
                    - status: Current payment status
                    - requires_action: True if 3DS needed
                    - amount/currency/receipt info if succeeded
        """
        try:
            # Validate currency and amount
            currency = payment_data.get('currency', '').lower()
            amount = payment_data.get('amount', 0)

            if currency != 'sgd':
                return None, "Only SGD currency is supported"

            if amount < PaymentService.MINIMUM_AMOUNTS['sgd']:
                return None, f"Amount below minimum of {PaymentService.MINIMUM_AMOUNTS['sgd']} cents"

            # Validate request data
            payment_request = PaymentRequest(**payment_data)
            data = payment_request.dict()

            # Prepare idempotency key
            idempotency = {'idempotency_key': idempotency_key} if idempotency_key else {}
            
            # Create payment intent with proper error handling
            try:
                intent = stripe.PaymentIntent.create(
                    amount=data['amount'],
                    currency=data['currency'],
                    payment_method=data['payment_method'],
                    confirmation_method='manual',
                    confirm=True,
                    description=data.get('description', 'Payment from billing service'),
                    metadata=data.get('metadata', {}),
                    receipt_email=data.get('customer_email'),
                    **idempotency
                )
            except stripe.error.CardError as e:
                logger.warning(f"Card error: {str(e)}")
                return None, f"Card error: {e.user_message}"
            except stripe.error.InvalidRequestError as e:
                logger.error(f"Invalid request: {str(e)}")
                return None, "Invalid payment details provided"
            
            # Build response based on payment status
            response = {
                'payment_intent_id': intent.id,
                'status': intent.status,
                'created': intent.created,
                'currency': intent.currency,
                'amount': intent.amount,
            }

            if intent.status == 'requires_action':
                response.update({
                    'requires_action': True,
                    'client_secret': intent.client_secret,
                    'next_action': intent.next_action
                })
            elif intent.status == 'succeeded':
                charge = intent.charges.data[0] if intent.charges.data else None
                response.update({
                    'success': True,
                    'receipt_email': intent.receipt_email,
                    'receipt_url': charge.receipt_url if charge else None,
                    'payment_method_details': charge.payment_method_details if charge else None,
                    'metadata': intent.metadata
                })
            elif intent.status == 'requires_payment_method':
                response.update({
                    'success': False,
                    'error': 'Payment method failed, please try another payment method'
                })
            else:
                response.update({
                    'success': False,
                    'error': f'Payment status: {intent.status}'
                })
            
            return response, None
            
        except stripe.error.AuthenticationError:
            logger.critical("Stripe authentication failed")
            return None, "Payment service configuration error"
        except stripe.error.APIConnectionError:
            logger.error("Could not connect to Stripe")
            return None, "Payment service temporarily unavailable"
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return None, "Payment processing error"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None, "An unexpected error occurred"

    @staticmethod
    def create_invoice(invoice_data: dict):
        """Create an invoice through Stripe"""
        try:
            # Validate request data using Pydantic model
            invoice_request = InvoiceRequest(**invoice_data)
            
            # Create invoice through Stripe
            invoice = stripe.Invoice.create(**invoice_request.dict())
            
            return invoice, None
            
        except Exception as e:
            logger.error(f"Invoice creation error: {str(e)}")
            return None, str(e)

    @staticmethod
    def confirm_payment(payment_intent_id: str):
        """
        Confirm a payment intent that requires additional authentication (like 3D Secure).
        Used during the active payment flow when additional security steps are needed.
        
        Args:
            payment_intent_id (str): Stripe PaymentIntent ID (starts with 'pi_')
            
        Returns:
            tuple: (response_dict, error_str)
            - response_dict contains payment status and next steps if needed
            - error_str is None if successful, otherwise contains error message
        """
        try:
            # Confirm the payment intent
            intent = stripe.PaymentIntent.confirm(payment_intent_id)
            
            response = {
                'payment_intent_id': intent.id,
                'status': intent.status,
            }
            
            if intent.status == 'requires_action':
                response.update({
                    'requires_action': True,
                    'payment_intent_client_secret': intent.client_secret,
                })
            elif intent.status == 'succeeded':
                response.update({
                    'success': True,
                    'amount': intent.amount,
                    'currency': intent.currency,
                    'receipt_email': intent.receipt_email,
                    'receipt_url': intent.charges.data[0].receipt_url if intent.charges.data else None
                })
            else:
                response.update({
                    'success': False,
                    'error': 'Payment not completed'
                })
            
            return response, None
            
        except Exception as e:
            logger.error(f"Payment confirmation error: {str(e)}")
            return None, str(e)

    @staticmethod
    def get_payment(payment_intent_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Retrieve payment details from Stripe using Payment Intent.
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID (pi_...)
            
        Returns:
            tuple: (payment_details, error_str)
                payment_details includes full payment state and history
        """
        try:
            payment = stripe.PaymentIntent.retrieve(payment_intent_id)
            charge = payment.charges.data[0] if payment.charges.data else None
            
            response = {
                "payment_intent_id": payment.id,
                "amount": payment.amount,
                "currency": payment.currency,
                "status": payment.status,
                "created": payment.created,
                "metadata": payment.metadata,
                "payment_method": payment.payment_method,
                "description": payment.description,
                "canceled_at": payment.canceled_at,
                "cancellation_reason": payment.cancellation_reason
            }

            if charge:
                response.update({
                    "charge_id": charge.id,
                    "receipt_url": charge.receipt_url,
                    "payment_method_details": charge.payment_method_details,
                    "failure_code": charge.failure_code,
                    "failure_message": charge.failure_message,
                    "outcome": charge.outcome
                })
            
            return response, None
            
        except stripe.error.InvalidRequestError as e:
            logger.warning(f"Invalid payment intent ID: {str(e)}")
            return None, "Payment not found"
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return None, "Error retrieving payment"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None, "An unexpected error occurred"

    @staticmethod
    def verify_payment(payment_intent_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Verify the status of a completed payment using Payment Intent.
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID (pi_...)
            
        Returns:
            tuple: (verification_details, error_str)
                verification_details includes payment status and fraud detection info
        """
        try:
            payment = stripe.PaymentIntent.retrieve(payment_intent_id)
            charge = payment.charges.data[0] if payment.charges.data else None
            
            verification = {
                "payment_intent_id": payment.id,
                "verified": True,
                "status": payment.status,
                "is_paid": payment.status == 'succeeded',
                "amount": payment.amount,
                "currency": payment.currency,
                "created": payment.created,
                "livemode": payment.livemode,
            }

            if charge:
                verification.update({
                    "charge_id": charge.id,
                    "payment_method": charge.payment_method_details.type if hasattr(charge, 'payment_method_details') else None,
                    "risk_level": charge.outcome.risk_level if charge.outcome else None,
                    "risk_score": charge.outcome.risk_score if charge.outcome else None,
                    "seller_message": charge.outcome.seller_message if charge.outcome else None
                })
            
            return verification, None
            
        except stripe.error.InvalidRequestError as e:
            logger.warning(f"Invalid payment intent ID: {str(e)}")
            return None, "Payment not found"
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return None, "Error verifying payment"
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None, "An unexpected error occurred" 