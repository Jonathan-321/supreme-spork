"""
WSGI entry point for AgriFinance application.
"""
# Import the most basic application possible to ensure it works
from app_basic import app as application
print("Using ultra-basic AgriFinance application")

# This file will be used by gunicorn to run the application
if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5000, debug=True)