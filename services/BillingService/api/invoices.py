from flask import Blueprint, request, jsonify
from services.stripe_service import create_stripe_invoice

invoices_bp = Blueprint("invoices", __name__)

@invoices_bp.route("/create", methods=["POST"])
def create_invoice():
    data = request.get_json()
    try:
        invoice_response = create_stripe_invoice(data)
        return jsonify(invoice_response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400