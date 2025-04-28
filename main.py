"""
Main entry point for the AgriFinance application.
"""
from debug_app import app

# If this file is executed directly, run the application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)