from flask import Blueprint, request, jsonify
from services.stripe_service import create_stripe_payment

payments_bp = Blueprint('payments', __name__)

@payments_bp.route("/create", methods=["POST"])
def create_payment():
    data = request.get_json()
    try:
        result = create_stripe_payment(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400