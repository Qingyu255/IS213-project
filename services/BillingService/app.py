# app.py
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from routes.payment import payment_bp
from routes.refund import refund_bp
from routes.webhook import webhook_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS
CORS(app)

# Register blueprints for modular endpoints
app.register_blueprint(payment_bp, url_prefix="/api/payment")
app.register_blueprint(refund_bp, url_prefix="/api/refund")
app.register_blueprint(webhook_bp, url_prefix="/api/webhook")

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}")
    return jsonify({"error": str(e)}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "billing-service"}), 200

if __name__ == '__main__':
    logger.info("Starting Billing Service...")
    app.run(host='0.0.0.0', port=5001, debug=Config.DEBUG)