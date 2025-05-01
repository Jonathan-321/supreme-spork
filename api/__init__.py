"""
AgriFinance API package initialization.
This sets up the Flask application with API routes for the mobile-first approach.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('agrifinance_api')

# Initialize SQLAlchemy
from api.models.base import Base
db = SQLAlchemy(model_class=Base)

def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure the app
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("API_SECRET_KEY", "dev-secret-key"),
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///agrifinance.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={
            "pool_recycle": 300,
            "pool_pre_ping": True
        }
    )
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints
    from api.routes.farmer_routes import farmer_api
    from api.routes.farm_routes import farm_api
    from api.routes.loan_routes import loan_api
    from api.routes.weather_routes import weather_api
    from api.routes.credit_routes import credit_api
    
    app.register_blueprint(farmer_api, url_prefix='/api/farmers')
    app.register_blueprint(farm_api, url_prefix='/api/farms')
    app.register_blueprint(loan_api, url_prefix='/api/loans')
    app.register_blueprint(weather_api, url_prefix='/api/weather')
    app.register_blueprint(credit_api, url_prefix='/api/credit')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created or verified")
    
    @app.route('/api/health')
    def health_check():
        """API health check endpoint"""
        return {
            "status": "healthy",
            "version": "1.0.0",
            "environment": os.environ.get("FLASK_ENV", "development")
        }
    
    return app
