# routes/test_refund.py
from flask import Blueprint, request, jsonify
import stripe
import logging
from config import Config
from services.validation import RefundRequest
from pydantic import ValidationError

# Configure logging
logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = Config.STRIPE_SECRET_KEY

test_refund_bp = Blueprint('test_refund', __name__)

@test_refund_bp.route("/create", methods=['POST'])
def process_test_refund():
    """
    Process a test refund using Stripe
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
        refund = stripe.Refund.create(
            charge=refund_data.charge_id,
            amount=refund_data.amount,
            reason=refund_data.reason
        )
        
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

@test_refund_bp.route("/<refund_id>", methods=['GET'])
def get_test_refund(refund_id):
    """
    Get test refund details by ID
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
            "created": refund.created
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