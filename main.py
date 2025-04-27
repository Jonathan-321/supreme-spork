from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

# Configure Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure database (uncomment when ready)
# app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///agrifinance.db")
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# db = SQLAlchemy(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Add more routes as needed

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)