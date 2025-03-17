# app.py
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config

# Import routes
from routes.payment import payment_bp
from routes.refund import refund_bp
from routes.webhook import webhook_bp

def setup_logging():
    """Configure application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def register_blueprints(app):
    """Register all blueprints for the application"""
    app.register_blueprint(payment_bp, url_prefix="/api/payment")
    app.register_blueprint(refund_bp, url_prefix="/api/refund")
    app.register_blueprint(webhook_bp, url_prefix="/api/webhook")

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    
    register_blueprints(app)
    
    return app

# Initialize logging
logger = setup_logging()

# Create the application instance
app = create_app()

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
    app.run(host='0.0.0.0', port=5001)