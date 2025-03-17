# routes/refund.py
from flask import Blueprint, request, jsonify
import stripe
import logging
from config import Config
from services.stripe_service import refund_stripe_payment
from services.validation import RefundRequest
from pydantic import ValidationError

# Configure logging
logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

refund_bp = Blueprint('refund', __name__)

# PRODUCTION ENDPOINTS

@refund_bp.route("/create", methods=['POST'])
def process_refund():
    """
    [PRODUCTION] Process a refund for a charge using Stripe
    ---
    Expected JSON body:
    {
        "charge_id": "ch_123456789",
        "amount": 1000,  # Optional: Amount in cents (if partial refund)
        "reason": "requested_by_customer"  # Optional: Reason for refund
    }
    """
    try:
        # Validate request data
        try:
            data = request.get_json()
            refund_data = RefundRequest(**data)
        except ValidationError as e:
            logger.error(f"Validation error: {e}")
            return jsonify({"error": str(e)}), 400
            
        # Process refund
        refund = refund_stripe_payment(refund_data.dict())
        
        return jsonify({
            "success": True,
            "refund_id": refund.id,
            "amount": refund.amount,
            "currency": refund.currency,
            "status": refund.status
        }), 200
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Refund processing error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@refund_bp.route("/payment_intent", methods=['POST'])
def refund_payment_intent():
    """
    [PRODUCTION] Process a refund for a payment intent using Stripe
    ---
    Expected JSON body:
    {
        "payment_intent_id": "pi_123456789",
        "amount": 1000,  # Optional: Amount in cents (if partial refund)
        "reason": "requested_by_customer",  # Optional: Reason for refund
        "metadata": {  # Optional: Additional metadata
            "refund_reason": "Customer request",
            "requested_by": "Support agent"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'payment_intent_id' not in data:
            return jsonify({"error": "Missing payment_intent_id parameter"}), 400
            
        # Get the payment intent to find its charge
        payment_intent = stripe.PaymentIntent.retrieve(data['payment_intent_id'])
        
        if not payment_intent.charges.data:
            return jsonify({"error": "No charges found for this payment intent"}), 400
            
        # Get the latest charge
        charge_id = payment_intent.charges.data[0].id
        
        # Prepare refund data
        refund_data = {
            'charge': charge_id,
            'reason': data.get('reason', 'requested_by_customer')
        }
        
        # Add amount if provided (for partial refunds)
        if 'amount' in data:
            refund_data['amount'] = data['amount']
            
        # Add metadata if provided
        if 'metadata' in data:
            refund_data['metadata'] = data['metadata']
            
        # Process the refund
        refund = stripe.Refund.create(**refund_data)
        
        return jsonify({
            "success": True,
            "refund_id": refund.id,
            "payment_intent_id": payment_intent.id,
            "amount": refund.amount,
            "currency": refund.currency,
            "status": refund.status
        }), 200
    except stripe.error.InvalidRequestError as e:
        logger.error(f"Invalid request: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Refund processing error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@refund_bp.route("/<refund_id>", methods=['GET'])
def get_refund(refund_id):
    """
    [PRODUCTION] Get refund details by ID
    ---
    Parameters:
      - refund_id: The Stripe refund ID
    """
    try:
        refund = stripe.Refund.retrieve(refund_id)
        return jsonify({
            "refund_id": refund.id,
            "amount": refund.amount,
            "currency": refund.currency,
            "status": refund.status,
            "charge_id": refund.charge,
            "reason": refund.reason,
            "created": refund.created,
            "metadata": refund.metadata
        }), 200
    except stripe.error.InvalidRequestError as e:
        logger.error(f"Invalid refund ID: {str(e)}")
        return jsonify({"error": "Refund not found"}), 404
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.error(f"Error retrieving refund: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500