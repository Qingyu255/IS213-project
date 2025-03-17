# routes/payment.py
from flask import Blueprint, request, jsonify, current_app
import stripe
import logging
from config import Config
from services.stripe_service import create_stripe_payment, create_stripe_invoice
from services.validation import PaymentRequest, InvoiceRequest
from pydantic import ValidationError

# Configure logging
logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

payment_bp = Blueprint('payment', __name__)

@payment_bp.route("/create", methods=['POST'])
def create_payment():
    """
    Create a payment using Stripe
    ---
    Expected JSON body:
    {
        "amount": 1000,  # Amount in cents
        "currency": "usd",
        "source": "tok_visa",
        "description": "Payment for Event #123"
    }
    """
    try:
        # Validate request data
        try:
            data = request.get_json()
            payment_data = PaymentRequest(**data)
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return jsonify({"error": str(e)}), 400
            
        # Process payment
        payment = create_stripe_payment(payment_data.dict())
        
        return jsonify({
            "success": True,
            "payment_id": payment.id,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status
        }), 200
    except stripe.error.CardError as e:
        # Card was declined
        logger.error(f"Card error: {e.user_message}")
        return jsonify({"error": e.user_message}), 400
    except stripe.error.StripeError as e:
        # Other Stripe errors
        logger.error(f"Stripe error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Payment creation error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@payment_bp.route("/invoice", methods=['POST'])
def create_invoice():
    """
    Create an invoice using Stripe
    ---
    Expected JSON body:
    {
        "customer_email": "customer@example.com",
        "amount": 1000,  # Amount in cents
        "currency": "usd",
        "description": "Invoice for Event #123"
    }
    """
    try:
        # Validate request data
        try:
            data = request.get_json()
            invoice_data = InvoiceRequest(**data)
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return jsonify({"error": str(e)}), 400
            
        # Create invoice
        invoice = create_stripe_invoice(invoice_data.dict())
        
        return jsonify({
            "success": True,
            "invoice_id": invoice.id,
            "customer_id": invoice.customer,
            "amount_due": invoice.amount_due,
            "status": invoice.status
        }), 200
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Invoice creation error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@payment_bp.route("/<payment_id>", methods=['GET'])
def get_payment(payment_id):
    """
    Get payment details by ID
    """
    try:
        payment = stripe.Charge.retrieve(payment_id)
        return jsonify({
            "payment_id": payment.id,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status,
            "created": payment.created
        }), 200
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Error retrieving payment: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500