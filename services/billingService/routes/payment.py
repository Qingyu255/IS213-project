# routes/payment.py
from flask import Blueprint, request, jsonify
import logging
from services.payment_service import PaymentService
from services.validation import PaymentRequest, validate_stripe_id
from functools import wraps
import uuid
import stripe
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

payment_bp = Blueprint('payment', __name__)

def require_json(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 415
        return f(*args, **kwargs)
    return decorated_function

def generate_idempotency_key():
    return str(uuid.uuid4())

@payment_bp.route("/process", methods=['POST'])
@require_json
def process_payment():
    """
    Process a payment using Stripe's Payment Intents API.
    
    Request body:
    {
        "amount": 50,  # Required: Amount in cents
        "currency": "sgd",  # Required: 3-letter ISO currency code
        "payment_method": "pm_...",  # Required: Stripe Payment Method ID
        "description": "Optional payment description",
        "metadata": {  # Optional: Additional data
            "order_id": "123",
            "customer_name": "John Doe"
        },
        "customer_email": "optional@email.com"  # Optional: Receipt email
    }
    
    Returns:
        200: {
            "payment": {
                "payment_intent_id": "pi_...",
                "status": "succeeded",
                "amount": 1000,
                "currency": "usd",
                "receipt_email": "customer@example.com",
                "receipt_url": "https://...",
                ...
            }
        }
        400: {"error": "Error message"}
        500: {"error": "Error message"}
    """
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            logger.warning("Missing request data")
            return jsonify({"error": "Missing request data"}), 400

        # Validate using Pydantic model
        try:
            payment_request = PaymentRequest(**data)
            validated_data = payment_request.dict()
        except Exception as e:
            logger.warning(f"Validation error: {str(e)}")
            return jsonify({"error": str(e)}), 400

        # Generate idempotency key for safe retries
        idempotency_key = request.headers.get('Idempotency-Key', generate_idempotency_key())
            
        payment, error = PaymentService.process_payment(validated_data, idempotency_key)
        if error:
            logger.warning(f"Payment processing failed: {error}")
            return jsonify({"error": error}), 400
            
        logger.info(f"Successfully processed payment: {payment['payment_intent_id']}")
        return jsonify({"payment": payment}), 200
        
    except Exception as e:
        logger.error(f"Payment endpoint error: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while processing the payment"}), 500

@payment_bp.route("/<payment_intent_id>", methods=['GET'])
def get_payment(payment_intent_id):
    """
    Retrieve payment details from Stripe.
    
    Parameters:
        payment_intent_id: Stripe Payment Intent ID (pi_...)
    
    Returns:
        200: {
            "payment_intent_id": "pi_...",
            "amount": 1000,
            "currency": "usd",
            "status": "succeeded",
            "created": 1234567890,
            "metadata": {},
            "receipt_url": "https://...",  # Optional
            "charge_id": "ch_...",
            "charge_status": "succeeded",
            "payment_method_details": {...},
            "failure_code": null,
            "failure_message": null,
            "outcome": {...}
        }
        400: {"error": "Invalid payment intent ID format"}
        404: {"error": "Payment not found"}
        500: {"error": "Error message"}
    """
    try:
        # Validate payment_intent_id format
        if not validate_stripe_id(payment_intent_id, 'pi_'):
            logger.warning(f"Invalid payment intent ID format: {payment_intent_id}")
            return jsonify({"error": "Invalid payment intent ID format"}), 400

        payment, error = PaymentService.get_payment(payment_intent_id)
        if error:
            logger.warning(f"Error retrieving payment: {error}")
            return jsonify({"error": error}), 404 if error == "Payment not found" else 500
            
        logger.info(f"Successfully retrieved payment: {payment_intent_id}")
        return jsonify(payment), 200
        
    except Exception as e:
        logger.error(f"Error retrieving payment: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while retrieving the payment"}), 500

@payment_bp.route("/verify", methods=['POST'])
@require_json
def verify_payment():
    """
    Verify payment status with Stripe.
    
    Request body:
    {
        "payment_intent_id": "pi_..."  # Required: Stripe Payment Intent ID
    }
    
    Returns:
        200: {
            "payment_intent_id": "pi_...",
            "verified": true,
            "status": "succeeded",
            "is_paid": true,
            "amount": 1000,
            "currency": "usd",
            "charge_id": "ch_...",
            "charge_status": "succeeded",
            "payment_method": "card",
            "risk_level": "normal",
            "risk_score": 0,
            "seller_message": "Payment complete.",
            "receipt_url": "https://..."  # Optional
        }
        400: {
            "verified": false,
            "error": "Missing payment_intent_id parameter"
        }
        404: {
            "verified": false,
            "error": "Payment not found"
        }
        500: {
            "verified": false,
            "error": "Error message"
        }
    """
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            logger.warning("Missing request data")
            return jsonify({
                "verified": False,
                "error": "Missing request data"
            }), 400
            
        if 'payment_intent_id' not in data:
            logger.warning("Missing payment_intent_id in request")
            return jsonify({
                "verified": False,
                "error": "Missing payment_intent_id parameter"
            }), 400
            
        # Validate payment_intent_id format
        if not validate_stripe_id(data['payment_intent_id'], 'pi_'):
            logger.warning(f"Invalid payment intent ID format: {data['payment_intent_id']}")
            return jsonify({
                "verified": False,
                "error": "Invalid payment intent ID format"
            }), 400
            
        result, error = PaymentService.verify_payment(data['payment_intent_id'])
        if error:
            logger.warning(f"Payment verification failed: {error}")
            return jsonify({
                "verified": False,
                "error": error
            }), 404 if error == "Payment not found" else 500
            
        logger.info(f"Successfully verified payment: {data['payment_intent_id']}")
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}", exc_info=True)
        return jsonify({
            "verified": False,
            "error": "An unexpected error occurred while verifying the payment"
        }), 500

@payment_bp.route("/verify-event-payment", methods=['POST'])
@require_json
def verify_event_payment():
    """
    Verify payment status for an event registration.
    
    Request body:
    {
        "event_id": "string",  # Required: Event ID
        "user_id": "string",   # Required: User ID
    }
    
    Returns:
        200: {
            "verified": true,
            "payment_intent_id": "pi_...",
            "amount": 1000,
            "currency": "sgd",
            "status": "succeeded",
            "event_id": "event_123",
            "user_id": "user_123",
            "payment_date": "2024-03-22T10:00:00Z"
        }
        404: {
            "verified": false,
            "error": "No payment found for this event registration"
        }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"verified": False, "error": "Missing request data"}), 400

        event_id = data.get('event_id')
        user_id = data.get('user_id')

        if not event_id or not user_id:
            return jsonify({"verified": False, "error": "Missing event_id or user_id"}), 400

        # Query Stripe for payments with matching metadata
        payments = stripe.PaymentIntent.list(
            limit=1,
            metadata={
                'event_id': event_id,
                'user_id': user_id
            }
        )

        if not payments.data:
            return jsonify({
                "verified": False,
                "error": "No payment found for this event registration"
            }), 404

        payment = payments.data[0]
        
        return jsonify({
            "verified": True,
            "payment_intent_id": payment.id,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "event_id": event_id,
            "user_id": user_id,
            "payment_date": datetime.fromtimestamp(payment.created).isoformat(),
            "can_refund": payment.status == "succeeded" and not payment.charges.data[0].refunded
        }), 200

    except Exception as e:
        logger.error(f"Error verifying event payment: {str(e)}", exc_info=True)
        return jsonify({
            "verified": False,
            "error": "An unexpected error occurred while verifying the payment"
        }), 500