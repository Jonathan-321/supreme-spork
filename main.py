from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
import os
from models import db, Region, Farmer, Farm, Crop, Loan, LoanProduct, User, WeatherData, NDVIData, ClimateRisk

# Configure Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
if not app.config["SQLALCHEMY_DATABASE_URI"]:
    # Fallback for development
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///agrifinance.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()
    
    # Add some initial data if database is empty
    if not Region.query.first():
        # Create a default region
        region = Region(name="Eastern Region", country="Ghana")
        db.session.add(region)
        
        # Create demo user and farmer
        user = User(
            username="demo_farmer",
            email="demo@agrifinance.com",
            password_hash="$2b$12$AZ5yBmkFiHYKSfKreSr.3.9A6eW3sGYYJvNK1HD6yQmNUCfgXhiVW",  # Demo password
            first_name="Demo",
            last_name="Farmer"
        )
        db.session.add(user)
        db.session.flush()
        
        farmer = Farmer(
            farmer_id="F-2025-001",
            type="INDIVIDUAL",
            phone_number="+233123456789",
            region=region,
            user=user
        )
        db.session.add(farmer)
        
        # Add some crops
        crop1 = Crop(
            name="Maize",
            scientific_name="Zea mays",
            growing_season_start=4,
            growing_season_end=8,
            water_requirement=500,
            temperature_min=10,
            temperature_max=35
        )
        
        crop2 = Crop(
            name="Cassava",
            scientific_name="Manihot esculenta",
            growing_season_start=3,
            growing_season_end=10,
            water_requirement=1000,
            temperature_min=20,
            temperature_max=30
        )
        
        db.session.add_all([crop1, crop2])
        db.session.flush()
        
        # Add farms
        farm1 = Farm(
            name="Riverside Farm",
            area=5.2,
            main_crop="Maize",
            secondary_crops="Beans, Groundnuts",
            soil_type="Sandy Loam",
            irrigation=True,
            farmer=farmer
        )
        
        farm2 = Farm(
            name="Hilltop Farm",
            area=3.8,
            main_crop="Cassava",
            secondary_crops="Sweet Potato",
            soil_type="Clay Loam",
            irrigation=False,
            farmer=farmer
        )
        
        db.session.add_all([farm1, farm2])
        
        # Add loan products
        loan_product1 = LoanProduct(
            name="Seasonal Crop Loan",
            description="Short-term financing for seasonal crop production needs including seeds, fertilizers, and labor.",
            min_amount=1000,
            max_amount=10000,
            interest_rate=12.0,
            term_months=12
        )
        
        loan_product2 = LoanProduct(
            name="Farm Equipment Loan",
            description="Medium-term financing for purchasing farm equipment and machinery.",
            min_amount=5000,
            max_amount=25000,
            interest_rate=15.0,
            term_months=36
        )
        
        db.session.add_all([loan_product1, loan_product2])
        db.session.flush()
        
        # Add loan products to crops
        loan_product1.allowed_crops.append(crop1)
        loan_product1.allowed_crops.append(crop2)
        loan_product2.allowed_crops.append(crop1)
        loan_product2.allowed_crops.append(crop2)
        
        # Create a loan
        loan = Loan(
            loan_id="L-2025-001",
            amount=5000,
            interest_rate=12.0,
            term_months=12,
            status="DISBURSED",
            purpose="Purchase seeds and fertilizer for maize production",
            farmer=farmer,
            product=loan_product1,
            farm=farm1,
            crop=crop1
        )
        
        db.session.add(loan)
        
        # Add weather data
        weather_data = WeatherData(
            date="2025-04-27",
            temperature_max=30.5,
            temperature_min=20.2,
            temperature_avg=24.0,
            precipitation=12.0,
            humidity=65.0,
            wind_speed=3.2,
            source="OpenWeatherMap",
            region=region
        )
        
        db.session.add(weather_data)
        
        # Add NDVI data
        ndvi_data1 = NDVIData(
            date="2025-04-27",
            ndvi_average=0.68,
            ndvi_min=0.45,
            ndvi_max=0.85,
            source="NASA MODIS",
            farm=farm1
        )
        
        ndvi_data2 = NDVIData(
            date="2025-04-27",
            ndvi_average=0.62,
            ndvi_min=0.40,
            ndvi_max=0.79,
            source="NASA MODIS",
            farm=farm2
        )
        
        db.session.add_all([ndvi_data1, ndvi_data2])
        
        # Add climate risk assessment
        climate_risk = ClimateRisk(
            risk_type="DROUGHT",
            risk_level="MEDIUM",
            assessment_date="2025-04-20",
            valid_until="2025-05-20",
            probability=0.45,
            potential_impact="Potential yield reduction of 20-30% if drought conditions persist",
            mitigation_measures="Implement irrigation where available, consider drought-resistant crop varieties",
            region=region
        )
        
        db.session.add(climate_risk)
        
        # Commit all changes
        db.session.commit()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    # Get the demo farmer for our demo
    farmer = Farmer.query.first()
    
    if not farmer:
        # If no farmer exists, redirect to home
        return redirect(url_for('home'))
    
    # Get farmer's active loans
    active_loans = Loan.query.filter(
        Loan.farmer_id == farmer.id,
        Loan.status.in_(['APPROVED', 'DISBURSED', 'REPAYING'])
    ).all()
    
    # Get farmer's farms
    farms = Farm.query.filter_by(farmer_id=farmer.id).all()
    
    # Get eligible loan products
    loan_products = LoanProduct.query.filter_by(is_active=True).all()
    
    # Get latest weather data for the region
    weather_data = WeatherData.query.filter_by(region_id=farmer.region_id).order_by(WeatherData.date.desc()).first()
    
    # Get latest NDVI data for each farm
    farm_ndvi_data = {}
    for farm in farms:
        ndvi = NDVIData.query.filter_by(farm_id=farm.id).order_by(NDVIData.date.desc()).first()
        if ndvi:
            farm_ndvi_data[farm.id] = ndvi
    
    # Get climate risk for the region
    climate_risk = ClimateRisk.query.filter_by(region_id=farmer.region_id).order_by(ClimateRisk.assessment_date.desc()).first()
    
    return render_template(
        'dashboard.html',
        farmer=farmer,
        active_loans=active_loans,
        farms=farms,
        loan_products=loan_products,
        weather_data=weather_data,
        farm_ndvi_data=farm_ndvi_data,
        climate_risk=climate_risk
    )

@app.route('/loans')
def loans():
    return render_template('loans.html')

@app.route('/farms')
def farms():
    return render_template('farms.html')

@app.route('/climate/dashboard')
def climate_dashboard():
    return render_template('climate/dashboard.html')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)