"""
Routes for data visualization in the AgriFinanceIntelligence platform.
"""
import os
import json
from flask import Blueprint, render_template, jsonify

# Create blueprint
visualization = Blueprint('visualization', __name__)

# Directory where scraped data is stored
DATA_DIR = "scraped_data"

@visualization.route('/visualization')
def visualization_dashboard():
    """Render the data visualization dashboard."""
    return render_template('data_visualization.html')

@visualization.route('/api/demo-data/weather')
def get_weather_data():
    """API endpoint to get weather data."""
    try:
        with open(os.path.join(DATA_DIR, "weather_data.json"), "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@visualization.route('/api/demo-data/ndvi')
def get_ndvi_data():
    """API endpoint to get NDVI data."""
    try:
        with open(os.path.join(DATA_DIR, "ndvi_data.json"), "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@visualization.route('/api/demo-data/crops')
def get_crop_data():
    """API endpoint to get crop price data."""
    try:
        with open(os.path.join(DATA_DIR, "crop_prices.json"), "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@visualization.route('/api/demo-data/loans')
def get_loan_data():
    """API endpoint to get loan data."""
    try:
        with open(os.path.join(DATA_DIR, "loan_data.json"), "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@visualization.route('/api/demo-data/credit')
def get_credit_data():
    """API endpoint to get credit score data."""
    try:
        with open(os.path.join(DATA_DIR, "credit_scores.json"), "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@visualization.route('/api/demo-data/climate')
def get_climate_data():
    """API endpoint to get climate risk data."""
    try:
        with open(os.path.join(DATA_DIR, "climate_risks.json"), "r") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
