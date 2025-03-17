# routes/payment.py
from flask import Blueprint, request, jsonify
import logging
from services.payment_service import PaymentService
from functools import wraps
import uuid

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
        "amount": 1000,  # Required: Amount in cents
        "currency": "usd",  # Required: 3-letter ISO currency code
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
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing request data"}), 400

        # Required fields validation
        required_fields = ['amount', 'currency', 'payment_method']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Generate idempotency key for safe retries
        idempotency_key = request.headers.get('Idempotency-Key', generate_idempotency_key())
            
        payment, error = PaymentService.process_payment(data, idempotency_key)
        if error:
            return jsonify({"error": error}), 400
            
        return jsonify({"payment": payment}), 200
        
    except Exception as e:
        logger.error(f"Payment endpoint error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

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
            ...
        }
        404: {"error": "Payment not found"}
        500: {"error": "Error message"}
    """
    try:
        # Validate payment_intent_id format
        if not payment_intent_id.startswith('pi_'):
            return jsonify({"error": "Invalid payment intent ID format"}), 400

        payment, error = PaymentService.get_payment(payment_intent_id)
        if error:
            return jsonify({"error": error}), 404 if error == "Payment not found" else 500
            
        return jsonify(payment), 200
        
    except Exception as e:
        logger.error(f"Error retrieving payment: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

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
            ...
        }
        400: {"error": "Missing payment_intent_id parameter"}
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
        data = request.get_json()
        
        if not data or 'payment_intent_id' not in data:
            return jsonify({
                "verified": False,
                "error": "Missing payment_intent_id parameter"
            }), 400

        # Validate payment_intent_id format
        if not data['payment_intent_id'].startswith('pi_'):
            return jsonify({
                "verified": False,
                "error": "Invalid payment intent ID format"
            }), 400
            
        result, error = PaymentService.verify_payment(data['payment_intent_id'])
        if error:
            return jsonify({
                "verified": False,
                "error": error
            }), 404 if error == "Payment not found" else 500
            
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        return jsonify({
            "verified": False,
            "error": "An unexpected error occurred"
        }), 500