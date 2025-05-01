"""
AgriFinance API Server
Main entry point for the mobile-first API backend.

This server provides the API endpoints for the AgriFinance mobile app,
focusing on farmer-centric design with offline capabilities.
"""
import os
from api import create_app
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('agrifinance_api_server')

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting AgriFinance API server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
