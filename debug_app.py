"""
Simplified application for debugging startup issues
"""
import os
import logging
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.logger.debug("Starting debug Flask application...")

# Configure secret key
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

@app.route('/')
def home():
    app.logger.debug("Debug home route accessed")
    return jsonify({"status": "ok", "message": "Debug application is running"})

@app.route('/health')
def health_check():
    app.logger.debug("Health check route accessed")
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)