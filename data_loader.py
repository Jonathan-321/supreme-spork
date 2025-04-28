"""
Database loader for AgriFinanceIntelligence platform.
This module loads scraped data into the application database.
"""
import os
import json
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """Loads scraped data into the AgriFinanceIntelligence database."""
    
    def __init__(self, app, db):
        """
        Initialize the data loader.
        
        Args:
            app: Flask application instance
            db: SQLAlchemy database instance
        """
        self.app = app
        self.db = db
        self.data_dir = "scraped_data"
        
    def load_all_data(self):
        """Load all scraped data into the database."""
        logger.info("Starting data loading process...")
        
        with self.app.app_context():
            try:
                # Import models here to avoid circular imports
                from models import (
                    Region, Crop, WeatherData, NDVIData, ClimateRisk, 
                    Farmer, Farm, Loan, CreditScore, CreditScoreComponent
                )
                
                # Clear existing data if needed
                # self._clear_existing_data()
                
                # Load regions
                regions = self._load_regions(Region)
                
                # Load crops
                crops = self._load_crops(Crop)
                
                # Load weather data
                self._load_weather_data(regions, WeatherData)
                
                # Load NDVI data
                self._load_ndvi_data(regions, NDVIData)
                
                # Load climate risks
                self._load_climate_risks(regions, ClimateRisk)
                
                # Load farmers and farms
                farmers = self._load_farmers_and_farms(regions, Farmer, Farm)
                
                # Load loans
                self._load_loans(farmers, crops, regions, Loan)
                
                # Load credit scores
                self._load_credit_scores(farmers, CreditScore, CreditScoreComponent)
                
                logger.info("Data loading complete!")
                return True
                
            except Exception as e:
                logger.error(f"Error loading data: {str(e)}")
                return False
    
    def _clear_existing_data(self):
        """Clear existing data from the database."""
        logger.info("Clearing existing data...")
        
        # Import models here to avoid circular imports
        from models import (
            Region, Crop, WeatherData, NDVIData, ClimateRisk, 
            Farmer, Farm, Loan, CreditScore, CreditScoreComponent
        )
        
        # Delete in reverse order of dependencies
        CreditScoreComponent.query.delete()
        CreditScore.query.delete()
        Loan.query.delete()
        Farm.query.delete()
        Farmer.query.delete()
        ClimateRisk.query.delete()
        NDVIData.query.delete()
        WeatherData.query.delete()
        Crop.query.delete()
        Region.query.delete()
        
        self.db.session.commit()
        logger.info("Existing data cleared.")
    
    def _load_regions(self, Region):
        """
        Load region data.
        
        Args:
            Region: Region model class
            
        Returns:
            dict: Dictionary of region objects by name
        """
        logger.info("Loading regions...")
        
        # Load region data from scraper
        try:
            with open(os.path.join(self.data_dir, "weather_data.json"), "r") as f:
                weather_data = json.load(f)
                
            regions = {}
            
            for region_key in weather_data.keys():
                region_name, country = region_key.split(", ")
                
                # Create region if it doesn't exist
                region = Region.query.filter_by(name=region_name, country=country).first()
                if not region:
                    region = Region(name=region_name, country=country)
                    self.db.session.add(region)
                
                regions[region_key] = region
            
            self.db.session.commit()
            logger.info(f"Loaded {len(regions)} regions.")
            return regions
            
        except Exception as e:
            logger.error(f"Error loading regions: {str(e)}")
            return {}
    
    def _load_crops(self, Crop):
        """
        Load crop data.
        
        Args:
            Crop: Crop model class
            
        Returns:
            dict: Dictionary of crop objects by name
        """
        logger.info("Loading crops...")
        
        # Load crop data from scraper
        try:
            with open(os.path.join(self.data_dir, "crop_prices.json"), "r") as f:
                crop_data = json.load(f)
                
            crops = {}
            
            for crop_name in crop_data.keys():
                # Create crop if it doesn't exist
                crop = Crop.query.filter_by(name=crop_name).first()
                if not crop:
                    # Set default values
                    if crop_name == "Maize":
                        crop = Crop(
                            name=crop_name,
                            scientific_name="Zea mays",
                            growing_season_start=3,
                            growing_season_end=8,
                            water_requirement=500.0,
                            temperature_min=10.0,
                            temperature_max=35.0
                        )
                    elif crop_name == "Rice":
                        crop = Crop(
                            name=crop_name,
                            scientific_name="Oryza sativa",
                            growing_season_start=4,
                            growing_season_end=9,
                            water_requirement=1200.0,
                            temperature_min=20.0,
                            temperature_max=35.0
                        )
                    elif crop_name == "Cassava":
                        crop = Crop(
                            name=crop_name,
                            scientific_name="Manihot esculenta",
                            growing_season_start=3,
                            growing_season_end=11,
                            water_requirement=400.0,
                            temperature_min=18.0,
                            temperature_max=35.0
                        )
                    elif crop_name == "Cocoa":
                        crop = Crop(
                            name=crop_name,
                            scientific_name="Theobroma cacao",
                            growing_season_start=9,
                            growing_season_end=2,
                            water_requirement=1500.0,
                            temperature_min=18.0,
                            temperature_max=32.0
                        )
                    elif crop_name == "Coffee":
                        crop = Crop(
                            name=crop_name,
                            scientific_name="Coffea arabica",
                            growing_season_start=10,
                            growing_season_end=3,
                            water_requirement=1200.0,
                            temperature_min=15.0,
                            temperature_max=30.0
                        )
                    elif crop_name == "Sorghum":
                        crop = Crop(
                            name=crop_name,
                            scientific_name="Sorghum bicolor",
                            growing_season_start=5,
                            growing_season_end=10,
                            water_requirement=350.0,
                            temperature_min=12.0,
                            temperature_max=37.0
                        )
                    else:
                        crop = Crop(
                            name=crop_name,
                            scientific_name=f"Scientific {crop_name}",
                            growing_season_start=3,
                            growing_season_end=9,
                            water_requirement=500.0,
                            temperature_min=15.0,
                            temperature_max=35.0
                        )
                    
                    self.db.session.add(crop)
                
                crops[crop_name] = crop
            
            self.db.session.commit()
            logger.info(f"Loaded {len(crops)} crops.")
            return crops
            
        except Exception as e:
            logger.error(f"Error loading crops: {str(e)}")
            return {}
    
    def _load_weather_data(self, regions, WeatherData):
        """
        Load weather data.
        
        Args:
            regions: Dictionary of region objects
            WeatherData: WeatherData model class
        """
        logger.info("Loading weather data...")
        
        try:
            with open(os.path.join(self.data_dir, "weather_data.json"), "r") as f:
                weather_data = json.load(f)
                
            total_records = 0
            
            for region_key, data_list in weather_data.items():
                if region_key not in regions:
                    continue
                    
                region = regions[region_key]
                
                for data in data_list:
                    date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                    
                    # Check if record already exists
                    existing = WeatherData.query.filter_by(
                        region=region,
                        date=date,
                        source='OpenWeatherMap'
                    ).first()
                    
                    if not existing:
                        weather_record = WeatherData(
                            region=region,
                            date=date,
                            temperature_max=data['temperature_max'],
                            temperature_min=data['temperature_min'],
                            temperature_avg=data['temperature_avg'],
                            precipitation=data['precipitation'],
                            humidity=data['humidity'],
                            wind_speed=data['wind_speed'],
                            source='OpenWeatherMap'
                        )
                        self.db.session.add(weather_record)
                        total_records += 1
            
            self.db.session.commit()
            logger.info(f"Loaded {total_records} weather records.")
            
        except Exception as e:
            logger.error(f"Error loading weather data: {str(e)}")
    
    def _load_ndvi_data(self, regions, NDVIData):
        """
        Load NDVI data.
        
        Args:
            regions: Dictionary of region objects
            NDVIData: NDVIData model class
        """
        logger.info("Loading NDVI data...")
        
        try:
            with open(os.path.join(self.data_dir, "ndvi_data.json"), "r") as f:
                ndvi_data = json.load(f)
                
            total_records = 0
            
            for region_key, data_list in ndvi_data.items():
                if region_key not in regions:
                    continue
                    
                region = regions[region_key]
                
                # Get farms in this region
                farms = []
                for farmer in region.farmers:
                    farms.extend(farmer.farms)
                
                if not farms:
                    continue
                
                for data in data_list:
                    date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                    
                    # Add NDVI data for each farm
                    for farm in farms:
                        # Check if record already exists
                        existing = NDVIData.query.filter_by(
                            farm=farm,
                            date=date,
                            source='NASA MODIS'
                        ).first()
                        
                        if not existing:
                            # Add some variation per farm
                            farm_variation = (hash(farm.name) % 20 - 10) / 100
                            ndvi_value = max(0, min(1, data['ndvi_value'] + farm_variation))
                            
                            ndvi_record = NDVIData(
                                farm=farm,
                                date=date,
                                ndvi_average=ndvi_value,
                                ndvi_min=max(0, ndvi_value - 0.1),
                                ndvi_max=min(1, ndvi_value + 0.1),
                                source='NASA MODIS'
                            )
                            self.db.session.add(ndvi_record)
                            total_records += 1
            
            self.db.session.commit()
            logger.info(f"Loaded {total_records} NDVI records.")
            
        except Exception as e:
            logger.error(f"Error loading NDVI data: {str(e)}")
    
    def _load_climate_risks(self, regions, ClimateRisk):
        """
        Load climate risk data.
        
        Args:
            regions: Dictionary of region objects
            ClimateRisk: ClimateRisk model class
        """
        logger.info("Loading climate risk data...")
        
        try:
            with open(os.path.join(self.data_dir, "climate_risks.json"), "r") as f:
                risk_data = json.load(f)
                
            total_records = 0
            
            for region_key, risks in risk_data.items():
                if region_key not in regions:
                    continue
                    
                region = regions[region_key]
                
                for risk in risks:
                    assessment_date = datetime.strptime(risk['assessment_date'], '%Y-%m-%d').date()
                    valid_until = datetime.strptime(risk['valid_until'], '%Y-%m-%d').date()
                    
                    # Check if record already exists
                    existing = ClimateRisk.query.filter_by(
                        region=region,
                        risk_type=risk['risk_type'],
                        assessment_date=assessment_date
                    ).first()
                    
                    if not existing:
                        risk_record = ClimateRisk(
                            region=region,
                            risk_type=risk['risk_type'],
                            risk_level=risk['risk_level'],
                            assessment_date=assessment_date,
                            valid_until=valid_until,
                            probability=risk['probability'],
                            potential_impact=risk['potential_impact'],
                            mitigation_measures=risk['mitigation_measures']
                        )
                        self.db.session.add(risk_record)
                        total_records += 1
            
            self.db.session.commit()
            logger.info(f"Loaded {total_records} climate risk records.")
            
        except Exception as e:
            logger.error(f"Error loading climate risk data: {str(e)}")
    
    def _load_farmers_and_farms(self, regions, Farmer, Farm):
        """
        Load farmer and farm data.
        
        Args:
            regions: Dictionary of region objects
            Farmer: Farmer model class
            Farm: Farm model class
            
        Returns:
            dict: Dictionary of farmer objects by ID
        """
        logger.info("Loading farmers and farms...")
        
        try:
            # Generate some farmers for each region
            farmers = {}
            total_farmers = 0
            total_farms = 0
            
            for region_key, region in regions.items():
                # Create 5-10 farmers per region
                num_farmers = min(10, max(5, hash(region_key) % 10))
                
                for i in range(num_farmers):
                    farmer_id = f"F{10000 + total_farmers}"
                    
                    # Check if farmer already exists
                    existing = Farmer.query.filter_by(farmer_id=farmer_id).first()
                    
                    if not existing:
                        # Randomly select farmer type
                        farmer_type = ['INDIVIDUAL', 'COOPERATIVE', 'SMALL_ENTERPRISE'][i % 3]
                        
                        farmer = Farmer(
                            farmer_id=farmer_id,
                            type=farmer_type,
                            phone_number=f"+233{700000000 + total_farmers}",
                            registration_date=datetime.now().date() - timedelta(days=365 * 2 + i * 30),
                            is_active=True,
                            region=region
                        )
                        self.db.session.add(farmer)
                        farmers[farmer_id] = farmer
                        total_farmers += 1
                        
                        # Create 1-3 farms for each farmer
                        num_farms = 1 + (hash(farmer_id) % 3)
                        
                        for j in range(num_farms):
                            farm_name = f"Farm {total_farms + 1}"
                            
                            farm = Farm(
                                name=farm_name,
                                area=round(5 + (hash(farm_name) % 20), 1),  # 5-25 hectares
                                main_crop=["Maize", "Rice", "Cassava", "Cocoa", "Coffee", "Sorghum"][j % 6],
                                secondary_crops="Vegetables, Beans",
                                soil_type=["Sandy Loam", "Clay Loam", "Silt Loam"][j % 3],
                                irrigation=(j % 3 == 0),  # 1/3 have irrigation
                                date_added=farmer.registration_date + timedelta(days=30),
                                farmer=farmer
                            )
                            self.db.session.add(farm)
                            total_farms += 1
            
            self.db.session.commit()
            logger.info(f"Loaded {total_farmers} farmers and {total_farms} farms.")
            return farmers
            
        except Exception as e:
            logger.error(f"Error loading farmers and farms: {str(e)}")
            return {}
    
    def _load_loans(self, farmers, crops, regions, Loan):
        """
        Load loan data.
        
        Args:
            farmers: Dictionary of farmer objects
            crops: Dictionary of crop objects
            regions: Dictionary of region objects
            Loan: Loan model class
        """
        logger.info("Loading loan data...")
        
        try:
            with open(os.path.join(self.data_dir, "loan_data.json"), "r") as f:
                loan_data = json.load(f)
                
            total_records = 0
            
            for loan_info in loan_data:
                loan_id = loan_info['loan_id']
                
                # Check if loan already exists
                existing = Loan.query.filter_by(loan_id=loan_id).first()
                
                if not existing:
                    # Find a farmer from the right region
                    region_name = loan_info['region']
                    country = loan_info['country']
                    region_key = f"{region_name}, {country}"
                    
                    if region_key not in regions:
                        continue
                        
                    region = regions[region_key]
                    
                    # Find farmers in this region
                    region_farmers = [f for f in farmers.values() if f.region == region]
                    
                    if not region_farmers:
                        continue
                        
                    farmer = region_farmers[hash(loan_id) % len(region_farmers)]
                    
                    # Find a farm for this farmer that grows the crop
                    crop_name = loan_info['crop']
                    matching_farms = [f for f in farmer.farms if f.main_crop == crop_name]
                    
                    if not matching_farms:
                        # Use any farm
                        if not farmer.farms:
                            continue
                        farm = farmer.farms[0]
                    else:
                        farm = matching_farms[0]
                    
                    # Find the crop
                    crop = None
                    for c in crops.values():
                        if c.name == crop_name:
                            crop = c
                            break
                    
                    if not crop:
                        continue
                    
                    # Parse dates
                    application_date = datetime.strptime(loan_info['application_date'], '%Y-%m-%d').date()
                    
                    approval_date = None
                    if loan_info['approval_date']:
                        approval_date = datetime.strptime(loan_info['approval_date'], '%Y-%m-%d').date()
                        
                    disbursement_date = None
                    if loan_info['disbursement_date']:
                        disbursement_date = datetime.strptime(loan_info['disbursement_date'], '%Y-%m-%d').date()
                        
                    expected_completion_date = None
                    if loan_info['expected_completion_date']:
                        expected_completion_date = datetime.strptime(loan_info['expected_completion_date'], '%Y-%m-%d').date()
                        
                    actual_completion_date = None
                    if loan_info['actual_completion_date']:
                        actual_completion_date = datetime.strptime(loan_info['actual_completion_date'], '%Y-%m-%d').date()
                    
                    loan = Loan(
                        loan_id=loan_id,
                        amount=loan_info['amount'],
                        interest_rate=loan_info['interest_rate'],
                        term_months=loan_info['term_months'],
                        status=loan_info['status'],
                        purpose=loan_info['purpose'],
                        application_date=application_date,
                        approval_date=approval_date,
                        disbursement_date=disbursement_date,
                        expected_completion_date=expected_completion_date,
                        actual_completion_date=actual_completion_date,
                        farmer=farmer,
                        farm=farm,
                        crop=crop
                    )
                    self.db.session.add(loan)
                    total_records += 1
            
            self.db.session.commit()
            logger.info(f"Loaded {total_records} loan records.")
            
        except Exception as e:
            logger.error(f"Error loading loan data: {str(e)}")
    
    def _load_credit_scores(self, farmers, CreditScore, CreditScoreComponent):
        """
        Load credit score data.
        
        Args:
            farmers: Dictionary of farmer objects
            CreditScore: CreditScore model class
            CreditScoreComponent: CreditScoreComponent model class
        """
        logger.info("Loading credit score data...")
        
        try:
            with open(os.path.join(self.data_dir, "credit_scores.json"), "r") as f:
                credit_data = json.load(f)
                
            total_scores = 0
            total_components = 0
            
            for score_info in credit_data:
                farmer_id = score_info['farmer_id']
                
                # Find matching farmer
                farmer = None
                for f in farmers.values():
                    if f.farmer_id == farmer_id:
                        farmer = f
                        break
                
                if not farmer:
                    # Use any farmer
                    if farmers:
                        farmer = list(farmers.values())[hash(farmer_id) % len(farmers)]
                    else:
                        continue
                
                # Parse dates
                generation_date = datetime.strptime(score_info['generation_date'], '%Y-%m-%d')
                valid_until = datetime.strptime(score_info['valid_until'], '%Y-%m-%d')
                
                # Check if score already exists
                existing = CreditScore.query.filter_by(
                    farmer=farmer,
                    date_generated=generation_date
                ).first()
                
                if not existing:
                    credit_score = CreditScore(
                        score=score_info['score'],
                        algorithm_version="1.0",
                        date_generated=generation_date,
                        valid_until=valid_until,
                        farmer=farmer
                    )
                    self.db.session.add(credit_score)
                    total_scores += 1
                    
                    # Add components
                    for component in score_info['components']:
                        component_record = CreditScoreComponent(
                            component_name=component['name'],
                            component_value=component['value'],
                            weight=component['weight'],
                            description=f"Contribution of {component['name']} to overall credit score",
                            credit_score=credit_score
                        )
                        self.db.session.add(component_record)
                        total_components += 1
            
            self.db.session.commit()
            logger.info(f"Loaded {total_scores} credit scores with {total_components} components.")
            
        except Exception as e:
            logger.error(f"Error loading credit scores: {str(e)}")

# Example usage
if __name__ == "__main__":
    from app import app, db
    
    loader = DataLoader(app, db)
    loader.load_all_data()
