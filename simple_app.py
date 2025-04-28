"""
Simplified AgriFinance application for Replit.
"""
import logging
import os
import sys
import traceback

from flask import Flask, render_template, redirect, url_for, request, flash, jsonify

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
app.secret_key = "dev-secret-key"

# Define routes
@app.route('/')
def home():
    try:
        logger.debug("Rendering home template")
        return render_template('home.html')
    except Exception as e:
        error_msg = f"Error rendering home template: {str(e)}"
        error_traceback = traceback.format_exc()
        logger.error(f"{error_msg}\n{error_traceback}")
        return f"Error: {str(e)}<br><pre>{error_traceback}</pre>", 500

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
        return f"Error: {str(e)}", 500

@app.route('/loans')
def loans():
    try:
        return render_template('loans.html')
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/farms')
def farms():
    try:
        return render_template('farms.html')
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/climate/dashboard')
def climate_dashboard():
    try:
        return render_template('climate/dashboard.html')
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/climate/alerts')
def climate_alerts():
    try:
        return render_template('climate/alerts.html')
    except Exception as e:
        return f"Error: {str(e)}", 500
    
@app.route('/credit/prediction')
def credit_prediction():
    try:
        return render_template('credit/prediction_dashboard.html')
    except Exception as e:
        return f"Error: {str(e)}", 500
    
@app.route('/mobile/app')
def mobile_app_demo():
    try:
        return render_template('mobile/app_demo.html')
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/api/credit-score/<farmer_id>')
def get_credit_score(farmer_id):
    # Demo credit score data
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

@app.route('/health')
def health_check():
    logger.debug("Health check route accessed")
    try:
        template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
        template_exists = os.path.exists(template_dir)
        static_exists = os.path.exists(static_dir)
        
        template_files = os.listdir(template_dir) if template_exists else []
        static_files = os.listdir(static_dir) if static_exists else []
        
        return jsonify({
            "status": "ok", 
            "message": "Simple AgriFinance application is running",
            "diagnostics": {
                "template_dir_exists": template_exists,
                "static_dir_exists": static_exists,
                "template_files": template_files[:5],  # First 5 files
                "static_files": static_files[:5],      # First 5 files
                "python_version": sys.version,
                "working_directory": os.getcwd(),
                "environment": {k: v for k, v in os.environ.items() if k.startswith("FLASK_") or k in ["PORT", "HOST"]}
            }
        })
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error in health check: {str(e)}",
            "traceback": traceback.format_exc()
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)