"""
Payment endpoints for the billing service
"""
from flask import Blueprint, request, jsonify
import logging
import stripe
from config import Config

logger = logging.getLogger(__name__)

stripe.api_key = Config.STRIPE_SECRET_KEY

payment_bp = Blueprint('payment', __name__)

@payment_bp.route("/create", methods=['POST'])
def create_payment():
    """Create a payment intent"""
    try:
        data = request.json
        
        # Required fields
        amount = data.get('amount')
        currency = data.get('currency', 'sgd')
        
        # Optional fields
        metadata = data.get('metadata', {})
        description = data.get('description')
        
        if not amount:
            return jsonify({
                "success": False,
                "error": "Amount is required"
            }), 400
        
        # Create a Payment Intent
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            description=description,
            metadata=metadata
        )
        
        return jsonify({
            "success": True,
            "client_secret": payment_intent.client_secret,
            "payment_intent_id": payment_intent.id
        })
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred"
        }), 500

@payment_bp.route("/verify", methods=['POST'])
def verify_payment():
    """Verify a payment intent status"""
    try:
        data = request.json
        payment_intent_id = data.get('payment_intent_id')
        
        if not payment_intent_id:
            return jsonify({
                "success": False,
                "error": "Payment intent ID is required"
            }), 400
        
        # Retrieve the Payment Intent
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        return jsonify({
            "success": True,
            "status": payment_intent.status,
            "amount": payment_intent.amount,
            "currency": payment_intent.currency,
            "metadata": payment_intent.metadata
        })
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred"
        }), 500 