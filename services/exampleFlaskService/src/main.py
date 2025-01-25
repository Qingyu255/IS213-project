import os
import requests
from flask import Flask, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# TODO: Setup logging

SPRING_SERVICE_URL = "http://example-spring-service:8080"
@app.route("/")
def home():
    return "Hello from Flask!"

@app.route("/call-spring")
def call_spring():
    try:
        # Example GET request to the Spring Boot endpoint
        response = requests.get(f"{SPRING_SERVICE_URL}/api/hellospring")
        data = response.json()
        return jsonify({
            "message": "Success calling Spring!",
            "spring_response": data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
