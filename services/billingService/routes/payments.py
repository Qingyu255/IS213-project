from flask import Blueprint, request, jsonify
from http import HTTPStatus
import stripe
import os
from config import Config

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/create-session', methods=['POST'])
def create_session():
    """Create a Stripe payment session for either booking or event"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), HTTPStatus.BAD_REQUEST

        # Extract common required data
        amount = data.get('amount')
        currency = data.get('currency', 'sgd')
        success_url = data.get('success_url')
        cancel_url = data.get('cancel_url')
        customer_email = data.get('customer_email')

        # Check if this is a booking or event payment
        booking_id = data.get('booking_id')
        event_id = data.get('event_id')
        user_id = data.get('user_id')
        organizer_id = data.get('organizer_id')

        if not all([amount, success_url, cancel_url, customer_email]):
            return jsonify({"error": "Missing required fields"}), HTTPStatus.BAD_REQUEST
        
        if not booking_id and not event_id:
            return jsonify({"error": "Either booking_id or event_id must be provided"}), HTTPStatus.BAD_REQUEST

        # Configure Stripe
        stripe.api_key = Config.STRIPE_SECRET_KEY

        # Create metadata based on payment type
        metadata = {
            'user_id': user_id,
            'customer_email': customer_email
        }
        
        if booking_id:
            metadata['booking_id'] = booking_id
            item_name = f'Booking {booking_id}'
        else:
            metadata['event_id'] = event_id
            metadata['organizer_id'] = organizer_id
            item_name = f'Event {event_id}'

        # Create payment session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': currency,
                    'unit_amount': int(amount * 100),  # Convert to cents
                    'product_data': {
                        'name': item_name,
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
            metadata=metadata,
        )

        return jsonify({
            "url": session.url,
            "session_id": session.id
        }), HTTPStatus.OK

    except stripe.error.StripeError as e:
        return jsonify({"error": str(e)}), HTTPStatus.BAD_REQUEST
    except Exception as e:
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR 