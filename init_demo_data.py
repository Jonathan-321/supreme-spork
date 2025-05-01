"""
Initialize the AgriFinance API database with demo data.

This script creates sample farmers, farms, loans, and weather data
for demonstration and testing purposes.
"""
import os
import sys
from datetime import datetime, timedelta
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('init_demo_data')

# Add the project directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our API and models
from api import create_app
from api.models import (
    Farmer, FarmerType, 
    Farm, CropType,
    Loan, LoanType, LoanStatus, Payment,
    WeatherForecast, WeatherCondition, ClimateRiskAssessment, RiskLevel
)
from api import db

def create_demo_farmers(count=5):
    """Create sample farmers"""
    logger.info(f"Creating {count} demo farmers")
    
    farmers = []
    
    # Sample data for Ghana
    first_names = ["Kwame", "Ama", "Kofi", "Abena", "Kwesi", "Akua", "Yaw", "Afia", "Kojo", "Adwoa"]
    last_names = ["Mensah", "Osei", "Boateng", "Owusu", "Adjei", "Agyemang", "Antwi", "Asante", "Manu", "Addo"]
    locations = [
        "Accra, Ghana", "Kumasi, Ghana", "Tamale, Ghana", "Cape Coast, Ghana", 
        "Takoradi, Ghana", "Koforidua, Ghana", "Sunyani, Ghana", "Ho, Ghana"
    ]
    
    # Sample coordinates (approximate for Ghana)
    lat_range = (4.5, 11.0)  # Ghana latitude range
    lon_range = (-3.5, 1.2)  # Ghana longitude range
    
    for i in range(count):
        # Generate random data
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        location = random.choice(locations)
        
        # Generate a phone number in Ghana format (e.g., +233 20 123 4567)
        phone_prefix = random.choice(["20", "24", "27", "54", "55"])
        phone_number = f"+233 {phone_prefix} {random.randint(100, 999)} {random.randint(1000, 9999)}"
        
        # Generate coordinates
        latitude = random.uniform(*lat_range)
        longitude = random.uniform(*lon_range)
        
        # Generate registration date (between 1 month and 2 years ago)
        days_ago = random.randint(30, 730)
        registration_date = datetime.utcnow() - timedelta(days=days_ago)
        
        # Create farmer
        farmer = Farmer(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            farmer_type=random.choice(list(FarmerType)),
            location=location,
            latitude=latitude,
            longitude=longitude,
            registration_date=registration_date
        )
        
        db.session.add(farmer)
        farmers.append(farmer)
    
    # Commit to get IDs
    db.session.commit()
    logger.info(f"Created {len(farmers)} farmers")
    return farmers

def create_demo_farms(farmers, farms_per_farmer=1):
    """Create sample farms for each farmer"""
    logger.info(f"Creating farms for {len(farmers)} farmers")
    
    farms = []
    
    # Sample farm names and crops
    farm_name_prefixes = ["Green", "Sunny", "Golden", "Fertile", "Abundant", "Peaceful", "Prosperous", "Fruitful"]
    farm_name_suffixes = ["Fields", "Acres", "Farm", "Gardens", "Plantation", "Homestead", "Valley", "Ridge"]
    
    for farmer in farmers:
        # Number of farms for this farmer (1-3)
        num_farms = random.randint(1, farms_per_farmer)
        
        for i in range(num_farms):
            # Generate farm name
            farm_name = f"{random.choice(farm_name_prefixes)} {random.choice(farm_name_suffixes)}"
            if num_farms > 1:
                farm_name += f" {i+1}"
                
            # Generate farm size (1-20 hectares)
            size_hectares = round(random.uniform(1, 20), 1)
            
            # Select crops
            primary_crop = random.choice(list(CropType))
            
            # 50% chance of having a secondary crop
            secondary_crop = random.choice(list(CropType)) if random.random() > 0.5 else None
            
            # Ensure secondary crop is different from primary
            while secondary_crop == primary_crop:
                secondary_crop = random.choice(list(CropType))
            
            # Generate coordinates near farmer's location (within ~5km)
            latitude = farmer.latitude + random.uniform(-0.05, 0.05)
            longitude = farmer.longitude + random.uniform(-0.05, 0.05)
            
            # Generate NDVI data for some farms
            last_ndvi_value = round(random.uniform(0.3, 0.8), 2) if random.random() > 0.3 else None
            last_ndvi_date = datetime.utcnow() - timedelta(days=random.randint(1, 30)) if last_ndvi_value else None
            
            # Create farm
            farm = Farm(
                farmer_id=farmer.id,
                name=farm_name,
                size_hectares=size_hectares,
                primary_crop=primary_crop,
                secondary_crop=secondary_crop,
                location=farmer.location,
                latitude=latitude,
                longitude=longitude,
                registration_date=farmer.registration_date + timedelta(days=random.randint(1, 30)),
                last_ndvi_value=last_ndvi_value,
                last_ndvi_date=last_ndvi_date
            )
            
            db.session.add(farm)
            farms.append(farm)
    
    # Commit to get IDs
    db.session.commit()
    logger.info(f"Created {len(farms)} farms")
    return farms

def create_demo_loans(farmers):
    """Create sample loans for farmers"""
    logger.info(f"Creating loans for {len(farmers)} farmers")
    
    loans = []
    
    for farmer in farmers:
        # Number of loans for this farmer (0-3)
        num_loans = random.randint(0, 3)
        
        for i in range(num_loans):
            # Generate loan details
            loan_type = random.choice(list(LoanType))
            
            # Amount based on loan type
            if loan_type == LoanType.SEASONAL:
                amount = random.uniform(500, 5000)
            elif loan_type == LoanType.EQUIPMENT:
                amount = random.uniform(2000, 10000)
            elif loan_type == LoanType.INFRASTRUCTURE:
                amount = random.uniform(5000, 25000)
            elif loan_type == LoanType.EMERGENCY:
                amount = random.uniform(500, 3000)
            else:  # EXPANSION
                amount = random.uniform(10000, 50000)
            
            # Round to 2 decimal places
            amount = round(amount, 2)
            
            # Interest rate (5-20%)
            interest_rate = round(random.uniform(5, 20), 1)
            
            # Term in months
            if loan_type == LoanType.SEASONAL:
                term_months = random.randint(3, 9)
            elif loan_type == LoanType.EQUIPMENT:
                term_months = random.randint(12, 36)
            elif loan_type == LoanType.INFRASTRUCTURE:
                term_months = random.randint(24, 60)
            elif loan_type == LoanType.EMERGENCY:
                term_months = random.randint(6, 18)
            else:  # EXPANSION
                term_months = random.randint(36, 84)
            
            # Application date (between 1 month and 1 year ago)
            days_ago = random.randint(30, 365)
            application_date = datetime.utcnow() - timedelta(days=days_ago)
            
            # Determine status based on application date
            if days_ago < 7:
                status = LoanStatus.PENDING
                approval_date = None
                disbursement_date = None
                due_date = None
            elif days_ago < 14:
                status = random.choice([LoanStatus.APPROVED, LoanStatus.REJECTED])
                approval_date = application_date + timedelta(days=random.randint(3, 7))
                disbursement_date = None
                due_date = None
            else:
                # Most loans should be active or completed
                status_options = [LoanStatus.DISBURSED, LoanStatus.REPAYING, LoanStatus.COMPLETED]
                if random.random() < 0.1:  # 10% chance of default
                    status_options.append(LoanStatus.DEFAULTED)
                
                status = random.choice(status_options)
                approval_date = application_date + timedelta(days=random.randint(3, 7))
                disbursement_date = approval_date + timedelta(days=random.randint(3, 14))
                due_date = disbursement_date + timedelta(days=30 * term_months)
            
            # Credit score and climate risk factor
            credit_score = round(random.uniform(50, 90), 1)
            climate_risk_factor = round(random.uniform(0.1, 0.8), 2)
            
            # Create loan
            loan = Loan(
                farmer_id=farmer.id,
                loan_type=loan_type,
                amount=amount,
                interest_rate=interest_rate,
                term_months=term_months,
                status=status,
                application_date=application_date,
                approval_date=approval_date,
                disbursement_date=disbursement_date,
                due_date=due_date,
                credit_score=credit_score,
                climate_risk_factor=climate_risk_factor
            )
            
            db.session.add(loan)
            loans.append(loan)
    
    # Commit to get IDs
    db.session.commit()
    logger.info(f"Created {len(loans)} loans")
    
    # Create payments for active loans
    create_demo_payments(loans)
    
    return loans

def create_demo_payments(loans):
    """Create sample payments for loans"""
    payments = []
    
    payment_methods = ["Mobile Money", "Bank Transfer", "Cash", "Agent Collection"]
    
    for loan in loans:
        if loan.disbursement_date and loan.status in [LoanStatus.REPAYING, LoanStatus.COMPLETED]:
            # Calculate monthly payment (simple calculation)
            monthly_payment = loan.amount / loan.term_months
            
            # Calculate number of payments made
            if loan.status == LoanStatus.COMPLETED:
                # All payments made
                num_payments = loan.term_months
            else:
                # Some payments made
                months_since_disbursement = (datetime.utcnow() - loan.disbursement_date).days / 30
                num_payments = min(int(months_since_disbursement), loan.term_months - 1)
            
            # Create payments
            for i in range(int(num_payments)):
                payment_date = loan.disbursement_date + timedelta(days=30 * (i + 1))
                
                # Slight variation in payment amount
                amount = round(monthly_payment * random.uniform(0.95, 1.05), 2)
                
                # Create payment
                payment = Payment(
                    loan_id=loan.id,
                    amount=amount,
                    payment_date=payment_date,
                    payment_method=random.choice(payment_methods),
                    transaction_id=f"TXN-{random.randint(100000, 999999)}"
                )
                
                db.session.add(payment)
                payments.append(payment)
    
    db.session.commit()
    logger.info(f"Created {len(payments)} loan payments")
    return payments

def create_demo_weather_data(farms):
    """Create sample weather forecasts and climate risk assessments"""
    logger.info("Creating weather and climate data")
    
    # Create weather forecasts for some farms
    forecasts = []
    for farm in random.sample(farms, min(len(farms), 10)):
        # Weather conditions common in Ghana
        conditions = [
            WeatherCondition.SUNNY,
            WeatherCondition.PARTLY_CLOUDY,
            WeatherCondition.CLOUDY,
            WeatherCondition.LIGHT_RAIN,
            WeatherCondition.HEAVY_RAIN,
            WeatherCondition.THUNDERSTORM
        ]
        
        # Create a 5-day forecast
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for i in range(5):
            day = today + timedelta(days=i)
            condition = random.choice(conditions)
            
            # Temperature based on condition
            if condition in [WeatherCondition.SUNNY, WeatherCondition.PARTLY_CLOUDY]:
                temp_high = random.uniform(28, 34)
                temp_low = random.uniform(22, 26)
            elif condition in [WeatherCondition.CLOUDY, WeatherCondition.LIGHT_RAIN]:
                temp_high = random.uniform(25, 30)
                temp_low = random.uniform(20, 24)
            else:
                temp_high = random.uniform(22, 28)
                temp_low = random.uniform(18, 22)
            
            # Precipitation based on condition
            if condition == WeatherCondition.SUNNY:
                precip_chance = random.uniform(0, 0.1)
                precip_amount = 0
            elif condition == WeatherCondition.PARTLY_CLOUDY:
                precip_chance = random.uniform(0.1, 0.3)
                precip_amount = random.uniform(0, 2) if precip_chance > 0.2 else 0
            elif condition == WeatherCondition.CLOUDY:
                precip_chance = random.uniform(0.2, 0.5)
                precip_amount = random.uniform(0, 5) if precip_chance > 0.3 else 0
            elif condition == WeatherCondition.LIGHT_RAIN:
                precip_chance = random.uniform(0.5, 0.8)
                precip_amount = random.uniform(2, 10)
            elif condition == WeatherCondition.HEAVY_RAIN:
                precip_chance = random.uniform(0.8, 1.0)
                precip_amount = random.uniform(10, 30)
            else:  # THUNDERSTORM
                precip_chance = random.uniform(0.8, 1.0)
                precip_amount = random.uniform(15, 40)
            
            # Create forecast
            forecast = WeatherForecast(
                location=farm.location,
                latitude=farm.latitude,
                longitude=farm.longitude,
                forecast_date=day,
                condition=condition,
                temperature_high=round(temp_high, 1),
                temperature_low=round(temp_low, 1),
                precipitation_chance=round(precip_chance, 2),
                precipitation_amount=round(precip_amount, 1),
                humidity=round(random.uniform(60, 90), 1),
                wind_speed=round(random.uniform(5, 20), 1),
                farming_recommendation="Sample recommendation for demo data"
            )
            
            db.session.add(forecast)
            forecasts.append(forecast)
    
    # Create climate risk assessments for some farms
    assessments = []
    for farm in random.sample(farms, min(len(farms), 15)):
        # Base risk on random factors
        base_risk = random.uniform(0.2, 0.8)
        
        # Calculate specific risks
        drought_risk = min(1.0, base_risk * random.uniform(0.8, 1.2))
        flood_risk = min(1.0, base_risk * random.uniform(0.8, 1.2))
        pest_risk = min(1.0, base_risk * random.uniform(0.8, 1.2))
        
        # Calculate overall risk score (0-100)
        risk_score = round((drought_risk * 0.4 + flood_risk * 0.4 + pest_risk * 0.2) * 100)
        
        # Determine risk level
        risk_level = RiskLevel.MINIMAL
        if risk_score >= 80:
            risk_level = RiskLevel.EXTREME
        elif risk_score >= 60:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 40:
            risk_level = RiskLevel.MEDIUM
        elif risk_score >= 20:
            risk_level = RiskLevel.LOW
        
        # Create assessment
        assessment = ClimateRiskAssessment(
            farm_id=farm.id,
            assessment_date=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            risk_level=risk_level,
            risk_score=risk_score,
            drought_risk=round(drought_risk, 2),
            flood_risk=round(flood_risk, 2),
            pest_risk=round(pest_risk, 2),
            mitigation_strategies=[]  # Empty for demo data
        )
        
        db.session.add(assessment)
        assessments.append(assessment)
    
    db.session.commit()
    logger.info(f"Created {len(forecasts)} weather forecasts and {len(assessments)} climate risk assessments")
    return forecasts, assessments

def init_demo_data():
    """Initialize the database with demo data"""
    logger.info("Initializing demo data")
    
    # Create farmers
    farmers = create_demo_farmers(count=10)
    
    # Create farms
    farms = create_demo_farms(farmers, farms_per_farmer=2)
    
    # Create loans
    loans = create_demo_loans(farmers)
    
    # Create weather data
    forecasts, assessments = create_demo_weather_data(farms)
    
    logger.info("Demo data initialization complete")
    return {
        "farmers": len(farmers),
        "farms": len(farms),
        "loans": len(loans),
        "forecasts": len(forecasts),
        "assessments": len(assessments)
    }

if __name__ == "__main__":
    # Create the Flask app and context
    app = create_app()
    
    with app.app_context():
        # Check if database is already populated
        existing_farmers = db.session.query(Farmer).count()
        if existing_farmers > 0:
            logger.warning(f"Database already contains {existing_farmers} farmers. Skipping initialization.")
            sys.exit(0)
        
        # Initialize demo data
        results = init_demo_data()
        
        # Print summary
        print("Demo data initialization complete:")
        for key, value in results.items():
            print(f"  - {key}: {value}")
