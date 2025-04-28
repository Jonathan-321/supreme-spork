# This is a backup of the original main.py file

# Import the Flask app from app.py
from app import app

# Import necessary modules
import enum
import os
from datetime import datetime
from flask import render_template, jsonify
from app import db

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

# Keep definitions of routes only
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