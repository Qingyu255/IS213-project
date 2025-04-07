from flask import Blueprint, request, jsonify
from http import HTTPStatus
import logging
from models.booking_payment import BookingPayment
from models.payment_verification import PaymentVerification
from models import get_session

logger = logging.getLogger(__name__)

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/intent/<booking_id>', methods=['GET'])
def get_payment_intent(booking_id):
    """
    Get payment intent for a booking
    ---
    tags:
      - Payments
    parameters:
      - name: booking_id
        in: path
        type: string
        required: true
        description: ID of the booking
    responses:
      200:
        description: Payment intent found
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            payment_intent_id:
              type: string
              example: pi_3NKzXYC5aBCD1234
            amount:
              type: number
              example: 100.00
            status:
              type: string
              example: succeeded
      404:
        description: Payment verification not found
      500:
        description: Internal server error
    """
    logger.info(f"Getting payment intent for booking {booking_id}")
    try:
        with get_session() as session:
            bookingPayment = session.query(BookingPayment)\
                .filter_by(booking_id=booking_id)\
                .order_by(BookingPayment.created_at.desc())\
                .first()
            
            if bookingPayment:
                logger.info(f"Found bookingPayment for booking {booking_id}: payment_id={bookingPayment.payment_intent_id}")
                return jsonify({
                    "success": True,
                    "payment_intent_id": bookingPayment.payment_intent_id,
                    "amount": bookingPayment.amount,
                    "status": bookingPayment.status
                })
            
            logger.error(f"No payment verification found for booking {booking_id}")
            return jsonify({
                "success": False,
                "error": "Payment verification not found"
            }), HTTPStatus.BAD_REQUEST

    except Exception as e:
        logger.error(f"Error getting payment intent: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR 
    
@payments_bp.route('/<booking_id>/verify', methods=['GET'])
def verify_payment(booking_id):
    """
    Verify if payment has been made for a booking
    ---
    tags:
      - Payments
    parameters:
      - name: booking_id
        in: path
        type: string
        required: true
        description: ID of the booking
    responses:
      200:
        description: Payment verification result
        schema:
          type: object
          properties:
            is_paid:
              type: boolean
              example: true
            error:
              type: string
              example: null
    """
    try:
        with get_session() as session:
            payment = session.query(BookingPayment)\
            .filter_by(booking_id=booking_id)\
            .first()

        if payment:
            return jsonify({
                "is_paid": True,
                "error": None
                })


        return jsonify({
            "is_paid": False,
            "error": "Payment not found or not paid"
            })
    except Exception as e:
        return jsonify({
            "error": f"Failed to verify payment: {str(e)}"
        })
