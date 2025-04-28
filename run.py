"""
Simple startup script for running the application directly.
This can be used as an alternative to gunicorn in case of issues.
"""
from debug_app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)