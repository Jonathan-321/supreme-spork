from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
import enum
from datetime import datetime

# Configure Flask app
app = Flask(__name__)
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
    "pool_pre_ping": True,  # Check connection validity before using it
    "connect_args": {
        "sslmode": "require"  # Use SSL but don't verify certificate
    }
}

# Initialize database
db = SQLAlchemy(app)

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

class Region(db.Model):
    """Represents a geographical region"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    
    # Relationships
    farmers = db.relationship('Farmer', back_populates='region')
    weather_data = db.relationship('WeatherData', back_populates='region')
    weather_forecasts = db.relationship('WeatherForecast', back_populates='region')
    climate_risks = db.relationship('ClimateRisk', back_populates='region')

    def __repr__(self):
        return f"<Region {self.name}, {self.country}>"

class User(db.Model):
    """Represents a user account"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    farmer = db.relationship('Farmer', back_populates='user', uselist=False)

    def __repr__(self):
        return f"<User {self.username}>"

class Farmer(db.Model):
    """Represents a farmer or farming entity"""
    id = db.Column(db.Integer, primary_key=True)
    farmer_id = db.Column(db.String(20), unique=True, nullable=False)
    type = db.Column(db.Enum(FarmerType), nullable=False)
    phone_number = db.Column(db.String(20))
    registration_date = db.Column(db.Date, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Foreign keys
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    region = db.relationship('Region', back_populates='farmers')
    user = db.relationship('User', back_populates='farmer')
    farms = db.relationship('Farm', back_populates='farmer')
    loans = db.relationship('Loan', back_populates='farmer')
    credit_scores = db.relationship('CreditScore', back_populates='farmer')
    credit_history = db.relationship('CreditHistory', back_populates='farmer')

    def __repr__(self):
        return f"<Farmer {self.farmer_id}>"

class Farm(db.Model):
    """Represents a farm belonging to a farmer"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    area = db.Column(db.Float, nullable=False)  # in hectares
    main_crop = db.Column(db.String(100))
    secondary_crops = db.Column(db.String(255))
    soil_type = db.Column(db.String(100))
    irrigation = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.Date, default=datetime.utcnow)
    
    # Foreign keys
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'))
    
    # Relationships
    farmer = db.relationship('Farmer', back_populates='farms')
    harvests = db.relationship('Harvest', back_populates='farm')
    ndvi_data = db.relationship('NDVIData', back_populates='farm')
    loans = db.relationship('Loan', back_populates='farm')

    def __repr__(self):
        return f"<Farm {self.name} - {self.area} ha>"

class Crop(db.Model):
    """Represents a crop type with growing information"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    scientific_name = db.Column(db.String(100))
    growing_season_start = db.Column(db.Integer)  # Month number (1-12)
    growing_season_end = db.Column(db.Integer)    # Month number (1-12)
    water_requirement = db.Column(db.Float)       # mm per season
    temperature_min = db.Column(db.Float)         # Minimum temperature in °C
    temperature_max = db.Column(db.Float)         # Maximum temperature in °C
    
    # Relationships
    harvests = db.relationship('Harvest', back_populates='crop')
    loans = db.relationship('Loan', back_populates='crop')

    def __repr__(self):
        return f"<Crop {self.name}>"

class Harvest(db.Model):
    """Represents a harvest record for a farm"""
    id = db.Column(db.Integer, primary_key=True)
    harvest_date = db.Column(db.Date, nullable=False)
    yield_amount = db.Column(db.Float, nullable=False)
    yield_unit = db.Column(db.String(20), nullable=False)
    quality_rating = db.Column(db.Integer)  # 1-5 scale
    notes = db.Column(db.Text)
    
    # Foreign keys
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'))
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'))
    
    # Relationships
    farm = db.relationship('Farm', back_populates='harvests')
    crop = db.relationship('Crop', back_populates='harvests')

    def __repr__(self):
        return f"<Harvest {self.harvest_date}>"

# Association table for LoanProduct to Crop (many-to-many)
loan_product_crop = db.Table('loan_product_crop',
    db.Column('loan_product_id', db.Integer, db.ForeignKey('loan_product.id')),
    db.Column('crop_id', db.Integer, db.ForeignKey('crop.id'))
)

class LoanProduct(db.Model):
    """Represents a loan product offered by the platform"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    min_amount = db.Column(db.Float, nullable=False)
    max_amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    term_months = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    loans = db.relationship('Loan', back_populates='product')
    
    # Many-to-many relationship with Crop
    allowed_crops = db.relationship('Crop', secondary=loan_product_crop,
                                   backref=db.backref('loan_products', lazy='dynamic'))

    def __repr__(self):
        return f"<LoanProduct {self.name}>"

class Loan(db.Model):
    """Represents a loan issued to a farmer"""
    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.String(20), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    term_months = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(LoanStatus), nullable=False, default=LoanStatus.PENDING)
    purpose = db.Column(db.Text)
    application_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    approval_date = db.Column(db.Date)
    disbursement_date = db.Column(db.Date)
    expected_completion_date = db.Column(db.Date)
    actual_completion_date = db.Column(db.Date)
    
    # Foreign keys
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('loan_product.id'))
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'))
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'))
    
    # Relationships
    farmer = db.relationship('Farmer', back_populates='loans')
    product = db.relationship('LoanProduct', back_populates='loans')
    farm = db.relationship('Farm', back_populates='loans')
    crop = db.relationship('Crop', back_populates='loans')
    payments = db.relationship('Payment', back_populates='loan')
    climate_adjustments = db.relationship('LoanClimateAdjustment', back_populates='loan')
    credit_history_events = db.relationship('CreditHistory', back_populates='loan')

    def __repr__(self):
        return f"<Loan {self.loan_id} - {self.status.value}>"

class Payment(db.Model):
    """Represents a payment made on a loan"""
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_type = db.Column(db.String(50))
    reference_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    # Foreign keys
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))
    
    # Relationships
    loan = db.relationship('Loan', back_populates='payments')

    def __repr__(self):
        return f"<Payment {self.amount} for Loan {self.loan_id}>"

class WeatherStation(db.Model):
    """Represents a weather station"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    station_id = db.Column(db.String(50), unique=True, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    elevation = db.Column(db.Float)  # Elevation in meters
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    active = db.Column(db.Boolean, default=True)
    
    # Relationships
    weather_data = db.relationship('WeatherData', back_populates='station')

    def __repr__(self):
        return f"<WeatherStation {self.name}>"

class WeatherData(db.Model):
    """Stores historical weather data"""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    temperature_max = db.Column(db.Float)
    temperature_min = db.Column(db.Float)
    temperature_avg = db.Column(db.Float)
    precipitation = db.Column(db.Float)  # in mm
    humidity = db.Column(db.Float)       # in %
    wind_speed = db.Column(db.Float)     # in m/s
    source = db.Column(db.String(50), nullable=False)
    
    # Foreign keys
    station_id = db.Column(db.Integer, db.ForeignKey('weather_station.id'))
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    
    # Relationships
    station = db.relationship('WeatherStation', back_populates='weather_data')
    region = db.relationship('Region', back_populates='weather_data')

    def __repr__(self):
        return f"<WeatherData {self.date}>"

class WeatherForecast(db.Model):
    """Stores weather forecast data"""
    id = db.Column(db.Integer, primary_key=True)
    forecast_date = db.Column(db.Date, nullable=False)  # Date when forecast was made
    prediction_date = db.Column(db.Date, nullable=False)  # Date of the prediction
    temperature_max = db.Column(db.Float)
    temperature_min = db.Column(db.Float)
    precipitation_probability = db.Column(db.Float)  # in %
    precipitation_amount = db.Column(db.Float)      # in mm
    source = db.Column(db.String(50), nullable=False)
    
    # Foreign keys
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    
    # Relationships
    region = db.relationship('Region', back_populates='weather_forecasts')

    def __repr__(self):
        return f"<WeatherForecast {self.prediction_date}>"

class SatelliteImagery(db.Model):
    """Stores metadata for satellite imagery"""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    satellite = db.Column(db.String(50), nullable=False)
    imagery_type = db.Column(db.String(50), nullable=False)
    resolution = db.Column(db.Integer)  # in meters
    cloud_cover_percentage = db.Column(db.Float)
    url = db.Column(db.String(500))
    
    # Foreign keys
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    
    # Relationships
    ndvi_data = db.relationship('NDVIData', back_populates='imagery')

    def __repr__(self):
        return f"<SatelliteImagery {self.date}>"

class NDVIData(db.Model):
    """Stores NDVI data for farms"""
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    ndvi_average = db.Column(db.Float, nullable=False)  # -1 to 1
    ndvi_min = db.Column(db.Float)
    ndvi_max = db.Column(db.Float)
    source = db.Column(db.String(50), nullable=False)
    
    # Foreign keys
    farm_id = db.Column(db.Integer, db.ForeignKey('farm.id'))
    imagery_id = db.Column(db.Integer, db.ForeignKey('satellite_imagery.id'))
    
    # Relationships
    farm = db.relationship('Farm', back_populates='ndvi_data')
    imagery = db.relationship('SatelliteImagery', back_populates='ndvi_data')

    def __repr__(self):
        return f"<NDVIData {self.farm.name} - {self.date}>"

class ClimateRisk(db.Model):
    """Stores climate risk assessments for regions"""
    id = db.Column(db.Integer, primary_key=True)
    risk_type = db.Column(db.String(100), nullable=False)
    risk_level = db.Column(db.Enum(RiskLevel), nullable=False)
    assessment_date = db.Column(db.Date, nullable=False)
    valid_until = db.Column(db.Date)
    probability = db.Column(db.Float)  # 0-1
    potential_impact = db.Column(db.Text)
    mitigation_measures = db.Column(db.Text)
    
    # Foreign keys
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    
    # Relationships
    region = db.relationship('Region', back_populates='climate_risks')

    def __repr__(self):
        return f"<ClimateRisk {self.risk_type}>"

class LoanClimateAdjustment(db.Model):
    """Tracks adjustments made to loans based on climate risk factors"""
    id = db.Column(db.Integer, primary_key=True)
    adjustment_type = db.Column(db.String(20), nullable=False)
    adjustment_date = db.Column(db.Date, nullable=False)
    climate_event = db.Column(db.String(100), nullable=False)
    original_value = db.Column(db.Float, nullable=False)
    adjusted_value = db.Column(db.Float, nullable=False)
    justification = db.Column(db.Text)
    approved_by = db.Column(db.String(100))
    
    # Foreign keys
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))
    
    # Relationships
    loan = db.relationship('Loan', back_populates='climate_adjustments')

    def __repr__(self):
        return f"<LoanClimateAdjustment {self.adjustment_type}>"

class CreditScoreConfiguration(db.Model):
    """Configuration for credit scoring algorithm"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Weights for different components (0-1)
    repayment_history_weight = db.Column(db.Float, default=0.3)
    farm_productivity_weight = db.Column(db.Float, default=0.2)
    market_conditions_weight = db.Column(db.Float, default=0.1)
    relationship_length_weight = db.Column(db.Float, default=0.1)
    climate_risk_weight = db.Column(db.Float, default=0.3)

    def __repr__(self):
        return f"<CreditScoreConfiguration {self.name}>"

class CreditScore(db.Model):
    """Represents a credit score for a farmer"""
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)  # 0-100
    algorithm_version = db.Column(db.String(20), nullable=False)
    date_generated = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.Date)
    
    # Foreign keys
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'))
    
    # Relationships
    farmer = db.relationship('Farmer', back_populates='credit_scores')
    components = db.relationship('CreditScoreComponent', back_populates='credit_score')

    def __repr__(self):
        return f"<CreditScore {self.score}>"

class CreditScoreComponent(db.Model):
    """Represents a component of a credit score"""
    id = db.Column(db.Integer, primary_key=True)
    component_name = db.Column(db.String(100), nullable=False)
    component_value = db.Column(db.Float, nullable=False)  # 0-1
    weight = db.Column(db.Float, nullable=False)          # 0-1
    description = db.Column(db.Text)
    
    # Foreign keys
    credit_score_id = db.Column(db.Integer, db.ForeignKey('credit_score.id'))
    
    # Relationships
    credit_score = db.relationship('CreditScore', back_populates='components')

    def __repr__(self):
        return f"<CreditScoreComponent {self.component_name}>"

class CreditHistory(db.Model):
    """Tracks credit history events for farmers"""
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float)
    days_late = db.Column(db.Integer)
    notes = db.Column(db.Text)
    
    # Foreign keys
    farmer_id = db.Column(db.Integer, db.ForeignKey('farmer.id'))
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))
    
    # Relationships
    farmer = db.relationship('Farmer', back_populates='credit_history')
    loan = db.relationship('Loan', back_populates='credit_history_events')

    def __repr__(self):
        return f"<CreditHistory {self.event_type}>"

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
            type=FarmerType.INDIVIDUAL,
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
            status=LoanStatus.DISBURSED,
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
            risk_level=RiskLevel.MEDIUM,
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
    try:
        # Get the demo farmer for our demo
        farmer = Farmer.query.first()
        
        if not farmer:
            # For demo purposes, create a placeholder farmer
            return render_template(
                'dashboard.html', 
                farmer=None, 
                active_loans=[],
                farms=[],
                loan_products=[],
                credit_score={"score": 75, "level": "Good"},
                climate_risks=[],
                weather_data={},
                recent_payments=[],
                upcoming_payment=None,
                demo_mode=True
            )
        
        # Get farmer's active loans
        active_loans = Loan.query.filter(
            Loan.farmer_id == farmer.id,
            Loan.status.in_([LoanStatus.APPROVED, LoanStatus.DISBURSED, LoanStatus.REPAYING])
        ).all()
        
        # Get farmer's farms
        farms = Farm.query.filter_by(farmer_id=farmer.id).all()
        
        # Get eligible loan products
        loan_products = LoanProduct.query.filter_by(is_active=True).all()
    except Exception as e:
        # Log the error
        app.logger.error(f"Database error: {str(e)}")
        
        # Return a demo view for the dashboard
        return render_template(
            'dashboard.html', 
            error=str(e),
            farmer=None, 
            active_loans=[],
            farms=[],
            loan_products=[],
            credit_score={"score": 75, "level": "Good"},
            climate_risks=[],
            weather_data={},
            recent_payments=[],
            upcoming_payment=None,
            demo_mode=True
        )
    
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

@app.route('/climate/alerts')
def climate_alerts():
    return render_template('climate/alerts.html')
    
@app.route('/credit/prediction')
def credit_prediction():
    return render_template('credit/prediction_dashboard.html')
    
@app.route('/mobile/app')
def mobile_app_demo():
    return render_template('mobile/app_demo.html')

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