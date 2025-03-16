# routes/payment.py
from flask import Blueprint, request, jsonify, current_app
import stripe
from config import Config

stripe.api_key = Config.STRIPE_SECRET_KEY

payment_bp = Blueprint('payment', __name__)

@payment_bp.route("/", methods=['POST'])
def create_payment():
    try:
        data = request.get_json()
        # Expect JSON body with 'amount' (in smallest currency unit) and 'currency'
        amount = data.get('amount')
        currency = data.get('currency', 'usd')
        if not amount:
            return jsonify({'error': 'Amount is required'}), 400

        # Create a PaymentIntent with dynamic pricing
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            automatic_payment_methods={'enabled': True}
        )

        return jsonify({'clientSecret': payment_intent.client_secret}), 200
    except Exception as e:
        current_app.logger.error(f"Payment creation error: {e}")
        return jsonify({'error': str(e)}), 500