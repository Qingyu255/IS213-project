import logging
import stripe
from services.validation import PaymentRequest, validate_stripe_id
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
            payment_data (dict): Validated payment data from PaymentRequest model
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
            logger.info(f"Processing payment with data: {payment_data}")
            
            # Validate currency and amount
            currency = payment_data.get('currency', '').lower()
            amount = payment_data.get('amount', 0)

            if currency != 'sgd':
                return None, "Only SGD currency is supported"

            if amount < PaymentService.MINIMUM_AMOUNTS['sgd']:
                return None, f"Amount below minimum of {PaymentService.MINIMUM_AMOUNTS['sgd']} cents"

            # Prepare idempotency key
            idempotency = {'idempotency_key': idempotency_key} if idempotency_key else {}
            
            # Create payment intent with proper error handling
            try:
                # Create a payment intent with default options 
                logger.info(f"Creating payment intent with Stripe API")
                
                payment_intent_params = {
                    'amount': payment_data['amount'],
                    'currency': payment_data['currency'],
                    'payment_method': payment_data['payment_method'],
                    'confirm': True,
                    'automatic_payment_methods': {
                        'enabled': True,
                        'allow_redirects': 'always'  # Allow redirects for 3D Secure
                    }
                }
                
                # Add return URL for redirect-based payment methods
                payment_intent_params['return_url'] = f"{Config.FRONTEND_URL}/payment/success"
                
                # Add optional fields if provided
                if 'description' in payment_data and payment_data['description']:
                    payment_intent_params['description'] = payment_data['description']
                if 'metadata' in payment_data and payment_data['metadata']:
                    payment_intent_params['metadata'] = payment_data['metadata']
                if 'customer_email' in payment_data and payment_data['customer_email']:
                    payment_intent_params['receipt_email'] = payment_data['customer_email']
                if idempotency_key:
                    payment_intent_params['idempotency_key'] = idempotency_key
                
                # Log the parameters
                logger.info(f"Payment intent parameters: {payment_intent_params}")
                
                # Create the payment intent
                payment_intent = stripe.PaymentIntent.create(**payment_intent_params)
                logger.info(f"Created payment intent: {payment_intent.id}")

                # Check payment intent status and handle accordingly
                if payment_intent.status == 'succeeded':
                    logger.info(f"Payment succeeded immediately: {payment_intent.id}")
                    return {
                        'success': True,
                        'payment_intent_id': payment_intent.id,
                        'client_secret': payment_intent.client_secret,
                        'status': payment_intent.status,
                        'amount': payment_intent.amount,
                        'currency': payment_intent.currency,
                        'charge_id': payment_intent.charges.data[0].id if hasattr(payment_intent, 'charges') and payment_intent.charges.data else None,
                        'receipt_url': payment_intent.charges.data[0].receipt_url if hasattr(payment_intent, 'charges') and payment_intent.charges.data and hasattr(payment_intent.charges.data[0], 'receipt_url') else None
                    }, None
                elif payment_intent.status == 'requires_action':
                    logger.info(f"Payment requires additional action (3D Secure): {payment_intent.id}")
                    return {
                        'success': False,
                        'requires_action': True,
                        'payment_intent_id': payment_intent.id,
                        'client_secret': payment_intent.client_secret,
                        'status': payment_intent.status,
                        'next_action': payment_intent.next_action
                    }, None
                elif payment_intent.status == 'requires_payment_method':
                    logger.warning(f"Payment failed, requires new payment method: {payment_intent.id}")
                    return {
                        'success': False,
                        'payment_intent_id': payment_intent.id,
                        'status': payment_intent.status,
                        'error': 'Payment method failed, please try another payment method'
                    }, None
                else:
                    logger.info(f"Payment is processing: {payment_intent.id}")
                    return {
                        'success': False,
                        'payment_intent_id': payment_intent.id,
                        'client_secret': payment_intent.client_secret,
                        'status': payment_intent.status,
                        'message': 'Payment is being processed'
                    }, None

            except stripe.error.CardError as e:
                error_msg = f"Card error: {e.user_message}"
                logger.warning(f"{error_msg} - Code: {e.code}, Param: {e.param}")
                return None, error_msg
            except stripe.error.InvalidRequestError as e:
                error_msg = f"Invalid payment details: {str(e)}"
                logger.error(f"{error_msg} - Param: {e.param}")
                return None, error_msg
            except stripe.error.AuthenticationError as e:
                error_msg = f"Authentication failed with Stripe: {str(e)}"
                logger.critical(error_msg)
                return None, error_msg
            except stripe.error.APIConnectionError as e:
                error_msg = f"Network error while connecting to Stripe: {str(e)}"
                logger.error(error_msg)
                return None, error_msg
            except stripe.error.StripeError as e:
                error_msg = f"Payment processing error: {str(e)}"
                logger.error(error_msg)
                return None, error_msg
            except Exception as e:
                error_msg = f"Unexpected error during payment processing: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return None, error_msg
            
        except Exception as e:
            logger.error(f"Unexpected error in process_payment: {str(e)}", exc_info=True)
            return None, f"An unexpected error occurred: {str(e)}"

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
            logger.info(f"Retrieving payment details for payment_intent_id: {payment_intent_id}")
            
            payment = stripe.PaymentIntent.retrieve(payment_intent_id)
            logger.info(f"Successfully retrieved payment: {payment.id}")
            
            # Safely access charges data
            charge = None
            if hasattr(payment, 'charges') and payment.charges and payment.charges.data:
                charge = payment.charges.data[0]
            
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
                    "receipt_url": charge.receipt_url if hasattr(charge, 'receipt_url') else None,
                    "payment_method_details": charge.payment_method_details if hasattr(charge, 'payment_method_details') else None,
                    "failure_code": charge.failure_code if hasattr(charge, 'failure_code') else None,
                    "failure_message": charge.failure_message if hasattr(charge, 'failure_message') else None,
                    "outcome": charge.outcome if hasattr(charge, 'outcome') else None
                })
            
            return response, None
            
        except stripe.error.InvalidRequestError as e:
            logger.warning(f"Invalid payment intent ID: {str(e)}")
            return None, "Payment not found"
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
            logger.error(f"Unexpected error in get_payment: {str(e)}", exc_info=True)
            return None, "An unexpected error occurred while retrieving payment details"

    @staticmethod
    def verify_payment(payment_intent_id: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Verify the status of a completed payment using Payment Intent.
        Ensures that the payment has been charged and completed successfully.
        
        Args:
            payment_intent_id: Stripe PaymentIntent ID (pi_...)
            
        Returns:
            tuple: (verification_details, error_str)
                verification_details includes payment status and charge verification
        """
        try:
            logger.info(f"Verifying payment for payment_intent_id: {payment_intent_id}")
            
            payment = stripe.PaymentIntent.retrieve(payment_intent_id)
            logger.info(f"Successfully retrieved payment for verification: {payment.id}")
            
            # Check if payment has succeeded
            if payment.status != 'succeeded':
                logger.warning(f"Payment {payment.id} has not succeeded. Current status: {payment.status}")
                return None, f"Payment has not succeeded. Current status: {payment.status}"
            
            # Verify charge exists
            if not hasattr(payment, 'charges') or not payment.charges or not payment.charges.data:
                logger.warning(f"No charges found for payment {payment.id}")
                return None, "No charges found for this payment"
            
            charge = payment.charges.data[0]
            
            # Verify charge status
            if charge.status != 'succeeded':
                logger.warning(f"Charge {charge.id} has not succeeded. Current status: {charge.status}")
                return None, f"Charge has not succeeded. Current status: {charge.status}"
            
            verification = {
                "payment_intent_id": payment.id,
                "verified": True,
                "status": payment.status,
                "is_paid": True,
                "amount": payment.amount,
                "currency": payment.currency,
                "created": payment.created,
                "livemode": payment.livemode,
                "charge_id": charge.id,
                "charge_status": charge.status,
                "payment_method": charge.payment_method_details.type if hasattr(charge, 'payment_method_details') else None,
                "risk_level": charge.outcome.risk_level if charge.outcome and hasattr(charge.outcome, 'risk_level') else None,
                "risk_score": charge.outcome.risk_score if charge.outcome and hasattr(charge.outcome, 'risk_score') else None,
                "seller_message": charge.outcome.seller_message if charge.outcome and hasattr(charge.outcome, 'seller_message') else None,
                "receipt_url": charge.receipt_url if hasattr(charge, 'receipt_url') else None
            }
            
            logger.info(f"Payment {payment.id} verified successfully with charge {charge.id}")
            return verification, None
            
        except stripe.error.InvalidRequestError as e:
            logger.warning(f"Invalid payment intent ID: {str(e)}")
            return None, "Payment not found"
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
            logger.error(f"Unexpected error in verify_payment: {str(e)}", exc_info=True)
            return None, "An unexpected error occurred while verifying payment" 