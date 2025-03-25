from http import HTTPStatus
import logging
import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config

# Import routes
from routes.refund import refund_bp
from routes.webhook import webhook_bp
from routes.events import events_bp
from models import init_db

def setup_logging():
    """Configure application logging"""
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def register_blueprints(app):
    """Register all blueprints for the application"""
    app.register_blueprint(refund_bp, url_prefix="/api/refund")
    app.register_blueprint(webhook_bp, url_prefix="/api/webhook")
    app.register_blueprint(events_bp, url_prefix="/api/events")

def create_app(config_class=Config):
    """Application factory function"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Initialize CORS
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3000"],  # Add your frontend URL
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize the database
    init_db()
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    @app.errorhandler(HTTPStatus.BAD_REQUEST)
    def not_found_error(error):
        return jsonify({"error": "Not found"}), HTTPStatus.BAD_REQUEST

    @app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), HTTPStatus.INTERNAL_SERVER_ERROR

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), HTTPStatus.INTERNAL_SERVER_ERROR
    
    @app.route('/')
    def index():
        return 'Billing Service API'
    
    return app

# Initialize logging
logger = setup_logging()

# Create the application instance
app = create_app()

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Docker"""
    try:
        return jsonify({
            "status": "healthy",
            "service": "billing-service",
            "environment": os.getenv('FLASK_ENV', 'production')
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}", exc_info=True)
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), HTTPStatus.INTERNAL_SERVER_ERROR

if __name__ == '__main__':
    logger.info("Starting Billing Service...")
    port = int(os.getenv('PORT', HTTPStatus.INTERNAL_SERVER_ERROR1))
    app.run(host='0.0.0.0', port=port)