"""
Application configuration and initialization for the AgriFinance platform.
"""
import os
import logging
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import enum
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('app')

# Database setup
class Base(DeclarativeBase):
    pass

# Initialize the SQLAlchemy extension
db = SQLAlchemy(model_class=Base)

# Create the Flask app
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.logger.debug("Starting Flask application...")

# Import visualization routes
from data_visualization_routes import visualization
from mobile_app_routes import mobile_app

# Register blueprints
app.register_blueprint(visualization)
app.register_blueprint(mobile_app, url_prefix='/mobile')

# Configure secret key
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
if not app.config["SQLALCHEMY_DATABASE_URI"]:
    # Fallback for development
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agrifinance.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Configure SQLAlchemy connection pool settings
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,  # Recycle connections after 5 minutes
    "pool_pre_ping": True  # Check connection validity before using it
}

# Initialize the database with the app
db.init_app(app)

# Define models
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

# Define basic routes with error handling
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

# Add an API route for credit score
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

# Run the application
if __name__ == '__main__':
    with app.app_context():
        try:
            # Create all database tables
            db.create_all()
            app.logger.debug("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}")
    
    app.run(host='0.0.0.0', port=8080, debug=True)