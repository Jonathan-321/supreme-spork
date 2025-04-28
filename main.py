"""
Main entry point for the AgriFinance application.
"""
# Import from our basic application
from app_basic import app

# This file will be used by gunicorn to run the application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)