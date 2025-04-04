# routes/refund.py
# TODO: This file needs work for refund composite service
from flask import Blueprint, request, jsonify
import logging
from services.refund_service import RefundService
from services.validation import RefundRequest, validate_stripe_id

logger = logging.getLogger(__name__)

refund_bp = Blueprint('refund', __name__)

@refund_bp.route("/process", methods=['POST']) # TODO: Check if still needed
def process_refund():
    """
    Process a refund using Stripe's Payment Intents API
    ---
    tags:
      - Refunds
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - payment_intent_id
          properties:
            payment_intent_id:
              type: string
              description: Stripe Payment Intent ID
              example: pi_1H2J3K4L5M6N7O8P9Q0R1S2T
            amount:
              type: integer
              description: Amount in cents for partial refund
              example: 1000
            reason:
              type: string
              description: Reason for refund
              enum: [duplicate, fraudulent, requested_by_customer]
              example: requested_by_customer
            metadata:
              type: object
              description: Additional metadata
              example:
                refund_reason: Customer request
                requested_by: Support agent
    responses:
      200:
        description: Refund processed successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            refund_id:
              type: string
              example: re_1H2J3K4L5M6N7O8P9Q0R1S2T
            payment_intent_id:
              type: string
              example: pi_1H2J3K4L5M6N7O8P9Q0R1S2T
            charge_id:
              type: string
              example: ch_1H2J3K4L5M6N7O8P9Q0R1S2T
            amount:
              type: integer
              example: 1000
            currency:
              type: string
              example: usd
            status:
              type: string
              example: succeeded
            reason:
              type: string
              example: requested_by_customer
            created:
              type: integer
              example: 1234567890
            metadata:
              type: object
              example: {}
            receipt_url:
              type: string
              example: https://pay.stripe.com/receipts/...
      400:
        description: Bad request
        schema:
          type: object
          properties:
            error:
              type: string
              example: Missing payment_intent_id
      500:
        description: Server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: An unexpected error occurred
    """
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            logger.warning("Missing request data")
            return jsonify({"error": "Missing request data"}), 400
            
        # Validate using Pydantic model
        try:
            refund_request = RefundRequest(**data)
            validated_data = refund_request.dict()
        except Exception as e:
            logger.warning(f"Validation error: {str(e)}")
            return jsonify({"error": str(e)}), 400
            
        # Process the refund
        result, error = RefundService.process_refund(validated_data)
        if error:
            logger.warning(f"Refund processing failed: {error}")
            return jsonify({"error": error}), 400
            
        logger.info(f"Successfully processed refund: {result['refund_id']}")
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Refund endpoint error: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while processing the refund"}), 500

@refund_bp.route("/<refund_id>", methods=['GET'])
def get_refund(refund_id):
    """
    Get refund details by ID
    ---
    tags:
      - Refunds
    parameters:
      - name: refund_id
        in: path
        type: string
        required: true
        description: Stripe Refund ID (re_...)
        example: re_1H2J3K4L5M6N7O8P9Q0R1S2T
    responses:
      200:
        description: Refund details retrieved successfully
        schema:
          type: object
          properties:
            refund_id:
              type: string
              example: re_1H2J3K4L5M6N7O8P9Q0R1S2T
            charge_id:
              type: string
              example: ch_1H2J3K4L5M6N7O8P9Q0R1S2T
            payment_intent_id:
              type: string
              example: pi_1H2J3K4L5M6N7O8P9Q0R1S2T
            amount:
              type: integer
              example: 1000
            currency:
              type: string
              example: usd
            status:
              type: string
              example: succeeded
            reason:
              type: string
              example: requested_by_customer
            created:
              type: integer
              example: 1234567890
            metadata:
              type: object
              example: {}
            receipt_url:
              type: string
              example: https://pay.stripe.com/receipts/...
      400:
        description: Invalid refund ID format
        schema:
          type: object
          properties:
            error:
              type: string
              example: Invalid refund ID format
      404:
        description: Refund not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: Refund not found
      500:
        description: Server error
        schema:
          type: object
          properties:
            error:
              type: string
              example: An unexpected error occurred
    """
    try:
        # Validate refund_id format
        if not validate_stripe_id(refund_id, 're_'):
            logger.warning(f"Invalid refund ID format: {refund_id}")
            return jsonify({"error": "Invalid refund ID format"}), 400
            
        result, error = RefundService.get_refund(refund_id)
        if error:
            logger.warning(f"Error retrieving refund: {error}")
            return jsonify({"error": error}), 404 if error == "Refund not found" else 500
            
        logger.info(f"Successfully retrieved refund: {refund_id}")
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error retrieving refund: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred while retrieving the refund"}), 500

@refund_bp.route("/verify", methods=['POST'])
def verify_refund():
    """
    Verify the status of a refund
    ---
    tags:
      - Refunds
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - refund_id
          properties:
            refund_id:
              type: string
              description: Stripe Refund ID
              example: re_1H2J3K4L5M6N7O8P9Q0R1S2T
    responses:
      200:
        description: Refund verified successfully
        schema:
          type: object
          properties:
            refund_id:
              type: string
              example: re_1H2J3K4L5M6N7O8P9Q0R1S2T
            verified:
              type: boolean
              example: true
            status:
              type: string
              example: succeeded
            is_succeeded:
              type: boolean
              example: true
            amount:
              type: integer
              example: 1000
            currency:
              type: string
              example: usd
            charge_id:
              type: string
              example: ch_1H2J3K4L5M6N7O8P9Q0R1S2T
            payment_intent_id:
              type: string
              example: pi_1H2J3K4L5M6N7O8P9Q0R1S2T
            reason:
              type: string
              example: requested_by_customer
            created:
              type: integer
              example: 1234567890
            receipt_url:
              type: string
              example: https://pay.stripe.com/receipts/...
            charge_status:
              type: string
              example: succeeded
            charge_amount:
              type: integer
              example: 1000
            charge_refunded:
              type: boolean
              example: true
            charge_dispute:
              type: boolean
              example: false
      400:
        description: Bad request
        schema:
          type: object
          properties:
            verified:
              type: boolean
              example: false
            error:
              type: string
              example: Missing refund_id parameter
      404:
        description: Refund not found
        schema:
          type: object
          properties:
            verified:
              type: boolean
              example: false
            error:
              type: string
              example: Refund not found
      500:
        description: Server error
        schema:
          type: object
          properties:
            verified:
              type: boolean
              example: false
            error:
              type: string
              example: An unexpected error occurred
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
            
        if 'refund_id' not in data:
            logger.warning("Missing refund_id in request")
            return jsonify({
                "verified": False,
                "error": "Missing refund_id parameter"
            }), 400
            
        # Validate refund_id format
        if not validate_stripe_id(data['refund_id'], 're_'):
            logger.warning(f"Invalid refund ID format: {data['refund_id']}")
            return jsonify({
                "verified": False,
                "error": "Invalid refund ID format"
            }), 400
            
        result, error = RefundService.verify_refund(data['refund_id'])
        if error:
            logger.warning(f"Refund verification failed: {error}")
            return jsonify({
                "verified": False,
                "error": error
            }), 404 if error == "Refund not found" else 500
            
        logger.info(f"Successfully verified refund: {data['refund_id']}")
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error verifying refund: {str(e)}", exc_info=True)
        return jsonify({
            "verified": False,
            "error": "An unexpected error occurred while verifying the refund"
        }), 500