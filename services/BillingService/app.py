# app.py
from flask import Flask
from config import Config
from routes.payment import payment_bp
from routes.refund import refund_bp
from routes.webhook import webhook_bp

app = Flask(__name__)
app.config.from_object(Config)

# Register blueprints for modular endpoints
app.register_blueprint(payment_bp, url_prefix="/api/payment")
app.register_blueprint(refund_bp, url_prefix="/api/refund")
app.register_blueprint(webhook_bp, url_prefix="/api/webhook")

if __name__ == '__main__':
    app.run(port=5001, debug=True)