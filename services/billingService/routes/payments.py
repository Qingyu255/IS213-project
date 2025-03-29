from flask import Blueprint, request, jsonify
from http import HTTPStatus
import stripe
import os
from config import Config

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