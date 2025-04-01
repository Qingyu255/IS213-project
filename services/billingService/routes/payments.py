from flask import Blueprint, request, jsonify
from http import HTTPStatus
import stripe
import os
from config import Config
import logging
from models.booking_payment import BookingPayment
from models.payment_verification import PaymentVerification
from models import get_session

logger = logging.getLogger(__name__)

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/create-session', methods=['POST'])
def create_session():
    """Create a Stripe payment session"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), HTTPStatus.BAD_REQUEST

        # Extract data from request
        booking_id = data.get('booking_id')
        amount = data.get('amount')
        currency = data.get('currency')
        customer_email = data.get('customer_email')
        success_url = data.get('success_url')
        cancel_url = data.get('cancel_url')

        if not all([booking_id, amount, currency, customer_email, success_url, cancel_url]):
            return jsonify({"error": "Missing required fields"}), HTTPStatus.BAD_REQUEST

        # Configure Stripe
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

        # Create payment session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'unit_amount': int(amount * 100),  # Convert to cents
                    'product_data': {
                        'name': f'Booking {booking_id}',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
            metadata={
                'booking_id': booking_id,
            },
        )

        return jsonify({
            "url": session.url,
            "session_id": session.id
        }), HTTPStatus.OK

    except stripe.error.StripeError as e:
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR

@payments_bp.route('/store-intent-booking', methods=['POST'])
def store_payment_intent():
    logger.info("Received store payment intent request")
    try:
        data = request.json
        logger.info(f"Request data for booking {data.get('booking_id')}: {data}")

        if not data or not all([
            data.get('booking_id'),
            data.get('payment_intent_id'),
            data.get('amount'),
            data.get('currency')
        ]):
            missing = [k for k in ['booking_id', 'payment_intent_id', 'amount', 'currency'] if not data.get(k)]
            logger.error(f"Missing fields: {missing}")
            return jsonify({"error": f"Missing required fields: {missing}"}), 400

        # Create new booking payment record
        booking_payment = BookingPayment(
            booking_id=data['booking_id'],
            payment_intent_id=data['payment_intent_id'],
            amount=data['amount'],
            currency=data['currency'],
            status='paid',
            customer_email=data.get('customer_email'),
            customer_name=data.get('customer_name')
        )

        # Save to database
        with get_session() as session:
            session.add(booking_payment)
            session.commit()
            logger.info(f"Successfully stored payment intent {data['payment_intent_id']} for booking {data['booking_id']}")
            result = booking_payment.to_dict()
            logger.info(f"Stored record: {result}")

        return jsonify({
            "success": True,
            "data": result
        }), 200

    except Exception as e:
        logger.error(f"Error storing payment intent: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@payments_bp.route('/intent/<booking_id>', methods=['GET'])
def get_payment_intent(booking_id):
    logger.info(f"Getting payment intent for booking {booking_id}")
    try:
        with get_session() as session:
            verification = session.query(PaymentVerification)\
                .filter_by(booking_id=booking_id)\
                .order_by(PaymentVerification.created_at.desc())\
                .first()
            
            if verification:
                logger.info(f"Found verification for booking {booking_id}: payment_id={verification.payment_id}")
                return jsonify({
                    "success": True,
                    "payment_intent_id": verification.payment_id,
                    "amount": verification.amount,
                    "status": verification.status
                })
            
            logger.error(f"No payment verification found for booking {booking_id}")
            return jsonify({
                "success": False,
                "error": "Payment verification not found"
            }), 404

    except Exception as e:
        logger.error(f"Error getting payment intent: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500 