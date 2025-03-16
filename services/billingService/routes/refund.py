# routes/refund.py
from flask import Blueprint, request, jsonify, current_app
import stripe
from config import Config

stripe.api_key = Config.STRIPE_SECRET_KEY

refund_bp = Blueprint('refund', __name__)

@refund_bp.route("/", methods=['POST'])
def process_refund():
    try:
        data = request.get_json()
        payment_intent_id = data.get('paymentIntentId')
        if not payment_intent_id:
            return jsonify({'error': 'paymentIntentId is required'}), 400

        # Retrieve the PaymentIntent to get associated charge(s)
        payment_intent = stripe.paymentIntents.retrieve(payment_intent_id)
        if not payment_intent.charges.data:
            return jsonify({'error': 'No charges found for this PaymentIntent.'}), 400
        
        # Use the first charge to process the refund
        charge_id = payment_intent.charges.data[0].id
        refund = stripe.refunds.create({'charge': charge_id})
        
        return jsonify({'refund': refund}), 200
    except Exception as e:
        current_app.logger.error(f"Refund error: {e}")
        return jsonify({'error': str(e)}), 500