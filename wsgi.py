"""
WSGI entry point for AgriFinance application.
"""
# Import the applications - use debug_app for testing, agrifinance for full functionality
from debug_app import app as debug_application
from agrifinance import app as main_application

# Select which application to use
# For now, use the debug application while we resolve startup issues
application = debug_application

# Switch to the main application when ready
# application = main_application

# This file will be used by gunicorn to run the application
if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000, debug=True)