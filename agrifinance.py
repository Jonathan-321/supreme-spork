"""
Main application module for AgriFinance platform.
"""
import os
import logging
import enum
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database setup
class Base(DeclarativeBase):
    pass

# Initialize the SQLAlchemy extension
db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.logger.debug("Starting AgriFinance application...")

# Configure secret key
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure SQLAlchemy connection pool settings
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,  # Recycle connections after 5 minutes
    "pool_pre_ping": True,  # Check connection validity before using it
    "connect_args": {"connect_timeout": 10}  # Connection timeout
}

# Initialize the database with the app
db.init_app(app)

# Define enums
class FarmerType(enum.Enum):
    INDIVIDUAL = "Individual"
    COOPERATIVE = "Cooperative"
    SMALL_ENTERPRISE = "Small Enterprise"

class LoanStatus(enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    DISBURSED = "Disbursed"
    REPAYING = "Repaying"
    COMPLETED = "Completed"
    DEFAULTED = "Defaulted"
    REJECTED = "Rejected"

class RiskLevel(enum.Enum):
    MINIMAL = "Minimal"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    EXTREME = "Extreme"

# Define routes - with error handling
@app.route('/')
def home():
    app.logger.debug("Home route accessed")
    try:
        return render_template('home.html')
    except Exception as e:
        app.logger.error(f"Error rendering home.html: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/dashboard')
def dashboard():
    try:
        return render_template('dashboard.html', 
                              farmer=None, 
                              active_loans=[],
                              farms=[],
                              loan_products=[],
                              credit_score={"score": 75, "level": "Good"},
                              climate_risks=[],
                              weather_data={},
                              recent_payments=[],
                              upcoming_payment=None,
                              demo_mode=True)
    except Exception as e:
        app.logger.error(f"Error rendering dashboard: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/loans')
def loans():
    try:
        return render_template('loans.html')
    except Exception as e:
        app.logger.error(f"Error rendering loans: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/farms')
def farms():
    try:
        return render_template('farms.html')
    except Exception as e:
        app.logger.error(f"Error rendering farms: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/climate/dashboard')
def climate_dashboard():
    try:
        return render_template('climate/dashboard.html')
    except Exception as e:
        app.logger.error(f"Error rendering climate dashboard: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/climate/alerts')
def climate_alerts():
    try:
        return render_template('climate/alerts.html')
    except Exception as e:
        app.logger.error(f"Error rendering climate alerts: {str(e)}")
        return f"Error: {str(e)}", 500
    
@app.route('/credit/prediction')
def credit_prediction():
    try:
        return render_template('credit/prediction_dashboard.html')
    except Exception as e:
        app.logger.error(f"Error rendering credit prediction: {str(e)}")
        return f"Error: {str(e)}", 500
    
@app.route('/mobile/app')
def mobile_app_demo():
    try:
        return render_template('mobile/app_demo.html')
    except Exception as e:
        app.logger.error(f"Error rendering mobile app demo: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/api/credit-score/<farmer_id>')
def get_credit_score(farmer_id):
    # This would normally calculate or fetch the credit score
    # For demo purposes, we'll return a fixed score
    return jsonify({
        'score': 75,
        'components': [
            {'name': 'Repayment History', 'value': 0.8, 'weight': 0.3},
            {'name': 'Farm Productivity', 'value': 0.7, 'weight': 0.2},
            {'name': 'Market Conditions', 'value': 0.6, 'weight': 0.1},
            {'name': 'Relationship Length', 'value': 0.5, 'weight': 0.1},
            {'name': 'Climate Risk', 'value': 0.7, 'weight': 0.3}
        ]
    })

@app.route('/api/health')
def health_check():
    # Simple health check endpoint
    return jsonify({"status": "ok", "message": "AgriFinance application is running"})

# Import models at the application level to make them available for the db
def initialize_models():
    """Initialize database models and create tables if they don't exist."""
    with app.app_context():
        try:
            # This is a special import pattern to handle circular imports
            # The models will be imported when this function is called, not when the module is loaded
            import models
            # Create all database tables
            db.create_all()
            app.logger.debug("Database tables created successfully")
            return True
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
            return False

# Run the application
if __name__ == '__main__':
    initialize_models()
    app.run(host='0.0.0.0', port=5000, debug=True)