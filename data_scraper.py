"""
Data scraping module for AgriFinanceIntelligence platform.
This module provides functionality to fetch and generate realistic data for demonstration purposes.
"""
import os
import json
import random
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

class DataScraper:
    """Main class for scraping and generating data for the AgriFinanceIntelligence platform."""
    
    def __init__(self):
        """Initialize the data scraper with API keys and configuration."""
        self.weather_api_key = os.environ.get('OPENWEATHER_API_KEY', 'your_openweather_api_key')
        self.nasa_api_key = os.environ.get('NASA_API_KEY', 'your_nasa_api_key')
        self.worldbank_base_url = "https://api.worldbank.org/v2"
        self.fao_base_url = "http://www.fao.org/faostat/api"
        
        # Regions to scrape data for
        self.regions = [
            {"name": "Eastern Region", "country": "Ghana", "lat": 6.5735, "lon": 0.2396},
            {"name": "Ashanti Region", "country": "Ghana", "lat": 6.7470, "lon": -1.5209},
            {"name": "Northern Region", "country": "Ghana", "lat": 9.5439, "lon": -0.9057},
            {"name": "Western Region", "country": "Kenya", "lat": -0.3031, "lon": 34.7713},
            {"name": "Rift Valley", "country": "Kenya", "lat": 0.5683, "lon": 35.7516},
            {"name": "Central Region", "country": "Uganda", "lat": 0.3476, "lon": 32.5825},
        ]
        
        # Crops to include
        self.crops = [
            {"name": "Maize", "scientific_name": "Zea mays", "season_start": 3, "season_end": 8},
            {"name": "Rice", "scientific_name": "Oryza sativa", "season_start": 4, "season_end": 9},
            {"name": "Cassava", "scientific_name": "Manihot esculenta", "season_start": 3, "season_end": 11},
            {"name": "Cocoa", "scientific_name": "Theobroma cacao", "season_start": 9, "season_end": 2},
            {"name": "Coffee", "scientific_name": "Coffea arabica", "season_start": 10, "season_end": 3},
            {"name": "Sorghum", "scientific_name": "Sorghum bicolor", "season_start": 5, "season_end": 10},
        ]
        
    def fetch_weather_data(self, lat, lon, days_back=30):
        """
        Fetch historical weather data from OpenWeatherMap API.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            days_back (int): Number of days of historical data to fetch
            
        Returns:
            list: List of daily weather data
        """
        print(f"Fetching weather data for coordinates ({lat}, {lon})")
        
        # In a real implementation, this would use the OpenWeatherMap API
        # For demonstration, we'll generate realistic weather data
        weather_data = []
        
        base_temp = random.uniform(22, 28)  # Base temperature for tropical regions
        base_rain = random.uniform(0, 5)    # Base rainfall in mm
        
        for day in range(days_back):
            date = datetime.now() - timedelta(days=day)
            
            # Add some randomness and seasonal variation
            temp_variation = random.uniform(-3, 3)
            seasonal_factor = np.sin(np.pi * date.timetuple().tm_yday / 183) * 3
            
            temp_max = base_temp + temp_variation + seasonal_factor + random.uniform(0, 2)
            temp_min = base_temp + temp_variation + seasonal_factor - random.uniform(3, 5)
            temp_avg = (temp_max + temp_min) / 2
            
            # Rainfall - more in rainy season
            rain_seasonal = max(0, np.sin(np.pi * date.timetuple().tm_yday / 183) * 15)
            rainfall = max(0, base_rain + rain_seasonal + random.uniform(-2, 10))
            
            # Humidity correlates somewhat with rainfall
            humidity = min(95, max(50, 65 + rainfall * 2 + random.uniform(-10, 10)))
            
            weather_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'temperature_max': round(temp_max, 1),
                'temperature_min': round(temp_min, 1),
                'temperature_avg': round(temp_avg, 1),
                'precipitation': round(rainfall, 1),
                'humidity': round(humidity, 1),
                'wind_speed': round(random.uniform(2, 15), 1),
            })
        
        return weather_data
    
    def fetch_ndvi_data(self, lat, lon, days_back=30):
        """
        Fetch or generate NDVI (Normalized Difference Vegetation Index) data.
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            days_back (int): Number of days of historical data
            
        Returns:
            list: List of daily NDVI data
        """
        print(f"Fetching NDVI data for coordinates ({lat}, {lon})")
        
        # In a real implementation, this would use NASA's API
        # For demonstration, we'll generate realistic NDVI data
        ndvi_data = []
        
        # Base NDVI value - between 0 and 1, higher is greener vegetation
        base_ndvi = random.uniform(0.4, 0.7)
        
        for day in range(days_back):
            date = datetime.now() - timedelta(days=day)
            
            # Add seasonal variation and random noise
            seasonal_factor = np.sin(np.pi * date.timetuple().tm_yday / 183) * 0.15
            daily_variation = random.uniform(-0.05, 0.05)
            
            ndvi_value = max(0, min(1, base_ndvi + seasonal_factor + daily_variation))
            
            ndvi_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'ndvi_value': round(ndvi_value, 3),
            })
        
        return ndvi_data
    
    def fetch_crop_prices(self, crop_name, country, days_back=365):
        """
        Fetch or generate historical crop price data.
        
        Args:
            crop_name (str): Name of the crop
            country (str): Country name
            days_back (int): Number of days of historical data
            
        Returns:
            list: List of daily crop price data
        """
        print(f"Fetching price data for {crop_name} in {country}")
        
        # In a real implementation, this would use an agricultural price API
        # For demonstration, we'll generate realistic price data
        price_data = []
        
        # Base price depends on crop
        base_prices = {
            "Maize": random.uniform(150, 200),
            "Rice": random.uniform(300, 400),
            "Cassava": random.uniform(100, 150),
            "Cocoa": random.uniform(2000, 2500),
            "Coffee": random.uniform(1800, 2200),
            "Sorghum": random.uniform(120, 180),
        }
        
        base_price = base_prices.get(crop_name, random.uniform(100, 300))
        
        # Generate daily prices with trend and seasonality
        trend = random.uniform(-0.0001, 0.0002)  # Slight upward or downward trend
        
        for day in range(days_back):
            date = datetime.now() - timedelta(days=day)
            
            # Add seasonal variation, trend, and random noise
            seasonal_factor = np.sin(np.pi * date.timetuple().tm_yday / 183) * (base_price * 0.1)
            trend_factor = trend * day * base_price
            daily_variation = random.uniform(-base_price * 0.02, base_price * 0.02)
            
            price = max(base_price * 0.7, base_price + seasonal_factor - trend_factor + daily_variation)
            
            price_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'price': round(price, 2),
                'currency': 'USD',
                'unit': 'per ton'
            })
        
        return price_data
    
    def generate_loan_data(self, num_loans=100):
        """
        Generate realistic loan data.
        
        Args:
            num_loans (int): Number of loans to generate
            
        Returns:
            list: List of loan data
        """
        print(f"Generating {num_loans} loan records")
        
        loan_data = []
        
        # Loan statuses and their probabilities
        statuses = ["PENDING", "APPROVED", "DISBURSED", "REPAYING", "COMPLETED", "DEFAULTED", "REJECTED"]
        status_probs = [0.05, 0.1, 0.15, 0.4, 0.2, 0.05, 0.05]
        
        # Loan amounts by crop type
        crop_loan_ranges = {
            "Maize": (500, 2000),
            "Rice": (800, 3000),
            "Cassava": (400, 1500),
            "Cocoa": (1000, 5000),
            "Coffee": (1000, 4500),
            "Sorghum": (600, 2500),
        }
        
        for i in range(num_loans):
            # Select random crop and region
            crop = random.choice(self.crops)
            region = random.choice(self.regions)
            
            # Generate loan amount based on crop
            amount_range = crop_loan_ranges.get(crop["name"], (500, 3000))
            amount = round(random.uniform(*amount_range), 2)
            
            # Generate dates
            application_date = datetime.now() - timedelta(days=random.randint(30, 730))
            
            # Status determines other dates
            status = random.choices(statuses, status_probs)[0]
            
            approval_date = None
            disbursement_date = None
            expected_completion_date = None
            actual_completion_date = None
            
            if status != "PENDING" and status != "REJECTED":
                approval_date = application_date + timedelta(days=random.randint(5, 15))
                
            if status in ["DISBURSED", "REPAYING", "COMPLETED", "DEFAULTED"]:
                disbursement_date = approval_date + timedelta(days=random.randint(3, 10))
                term_months = random.choice([6, 12, 18, 24])
                expected_completion_date = disbursement_date + timedelta(days=term_months * 30)
                
            if status in ["COMPLETED", "DEFAULTED"]:
                if status == "COMPLETED":
                    # Completed loans might finish early or on time
                    days_early = random.randint(-10, 30)
                    actual_completion_date = expected_completion_date - timedelta(days=days_early)
                else:
                    # Defaulted loans typically default after some payments
                    default_after = random.uniform(0.3, 0.8)  # Default after 30-80% of term
                    term_days = (expected_completion_date - disbursement_date).days
                    actual_completion_date = disbursement_date + timedelta(days=int(term_days * default_after))
            
            loan_data.append({
                'loan_id': f"L{100000 + i}",
                'amount': amount,
                'interest_rate': round(random.uniform(5, 15), 2),
                'term_months': random.choice([6, 12, 18, 24]),
                'status': status,
                'purpose': f"{crop['name']} cultivation",
                'application_date': application_date.strftime('%Y-%m-%d'),
                'approval_date': approval_date.strftime('%Y-%m-%d') if approval_date else None,
                'disbursement_date': disbursement_date.strftime('%Y-%m-%d') if disbursement_date else None,
                'expected_completion_date': expected_completion_date.strftime('%Y-%m-%d') if expected_completion_date else None,
                'actual_completion_date': actual_completion_date.strftime('%Y-%m-%d') if actual_completion_date else None,
                'region': region['name'],
                'country': region['country'],
                'crop': crop['name']
            })
        
        return loan_data
    
    def generate_credit_scores(self, num_farmers=50):
        """
        Generate credit score data for farmers.
        
        Args:
            num_farmers (int): Number of farmers to generate credit scores for
            
        Returns:
            list: List of credit score data
        """
        print(f"Generating credit scores for {num_farmers} farmers")
        
        credit_data = []
        
        for i in range(num_farmers):
            # Base score between 300-850 (standard credit score range)
            base_score = random.randint(300, 850)
            
            # Components that make up the score
            repayment_history = random.uniform(0.3, 1.0)
            farm_productivity = random.uniform(0.3, 1.0)
            market_conditions = random.uniform(0.4, 1.0)
            relationship_length = random.uniform(0.2, 1.0)
            climate_risk = random.uniform(0.3, 1.0)
            
            # Weights for each component
            repayment_weight = 0.3
            productivity_weight = 0.2
            market_weight = 0.1
            relationship_weight = 0.1
            climate_weight = 0.3
            
            # Calculate weighted score
            weighted_score = (
                repayment_history * repayment_weight +
                farm_productivity * productivity_weight +
                market_conditions * market_weight +
                relationship_length * relationship_weight +
                climate_risk * climate_weight
            )
            
            # Adjust base score based on weighted components
            final_score = int(base_score * weighted_score)
            final_score = max(300, min(850, final_score))  # Ensure within range
            
            credit_data.append({
                'farmer_id': f"F{10000 + i}",
                'score': final_score,
                'generation_date': (datetime.now() - timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d'),
                'valid_until': (datetime.now() + timedelta(days=random.randint(90, 180))).strftime('%Y-%m-%d'),
                'components': [
                    {'name': 'Repayment History', 'value': round(repayment_history, 2), 'weight': repayment_weight},
                    {'name': 'Farm Productivity', 'value': round(farm_productivity, 2), 'weight': productivity_weight},
                    {'name': 'Market Conditions', 'value': round(market_conditions, 2), 'weight': market_weight},
                    {'name': 'Relationship Length', 'value': round(relationship_length, 2), 'weight': relationship_weight},
                    {'name': 'Climate Risk', 'value': round(climate_risk, 2), 'weight': climate_weight}
                ]
            })
        
        return credit_data
    
    def generate_climate_risks(self):
        """
        Generate climate risk assessments for regions.
        
        Returns:
            dict: Climate risk data by region
        """
        print("Generating climate risk assessments")
        
        risk_types = [
            "Drought", "Flooding", "Extreme Heat", "Pest Outbreak", 
            "Erratic Rainfall", "Soil Erosion", "Desertification"
        ]
        
        risk_levels = ["MINIMAL", "LOW", "MEDIUM", "HIGH", "EXTREME"]
        level_probs = [0.1, 0.25, 0.4, 0.2, 0.05]  # Probabilities for each level
        
        climate_risks = {}
        
        for region in self.regions:
            region_key = f"{region['name']}, {region['country']}"
            region_risks = []
            
            # Each region gets 3-5 risk assessments
            num_risks = random.randint(3, 5)
            selected_risks = random.sample(risk_types, num_risks)
            
            for risk_type in selected_risks:
                # Determine risk level with weighted probability
                risk_level = random.choices(risk_levels, level_probs)[0]
                
                # Assessment date within last 60 days
                assessment_date = datetime.now() - timedelta(days=random.randint(0, 60))
                
                # Valid for 3-12 months
                valid_months = random.randint(3, 12)
                valid_until = assessment_date + timedelta(days=valid_months * 30)
                
                # Probability of occurrence (0-1)
                probability = random.uniform(0.1, 0.9)
                
                region_risks.append({
                    'risk_type': risk_type,
                    'risk_level': risk_level,
                    'assessment_date': assessment_date.strftime('%Y-%m-%d'),
                    'valid_until': valid_until.strftime('%Y-%m-%d'),
                    'probability': round(probability, 2),
                    'potential_impact': self._generate_impact_description(risk_type, risk_level),
                    'mitigation_measures': self._generate_mitigation_measures(risk_type)
                })
            
            climate_risks[region_key] = region_risks
        
        return climate_risks
    
    def _generate_impact_description(self, risk_type, risk_level):
        """Generate a description of potential impacts based on risk type and level."""
        impact_templates = {
            "Drought": [
                "Reduced crop yields by {yield_loss}%.",
                "Water stress affecting plant growth and development.",
                "Increased irrigation costs of approximately ${cost} per hectare.",
                "Potential total loss for susceptible crops."
            ],
            "Flooding": [
                "Crop damage from waterlogging affecting {yield_loss}% of production.",
                "Soil nutrient leaching requiring additional fertilizer applications.",
                "Infrastructure damage to irrigation systems and farm roads.",
                "Delayed planting or harvesting operations by {days} days."
            ],
            "Extreme Heat": [
                "Heat stress reducing crop yields by {yield_loss}%.",
                "Increased water requirements for irrigation.",
                "Potential crop failure for heat-sensitive varieties.",
                "Reduced worker productivity during peak heat periods."
            ],
            "Pest Outbreak": [
                "Crop damage of {yield_loss}% if left untreated.",
                "Increased pesticide costs of ${cost} per hectare.",
                "Potential spread to neighboring farms.",
                "Quality degradation affecting market prices."
            ],
            "Erratic Rainfall": [
                "Unpredictable growing conditions affecting planning.",
                "Yield variability of ±{yield_loss}%.",
                "Challenges in timing planting and harvesting operations.",
                "Increased risk of either drought or flooding conditions."
            ],
            "Soil Erosion": [
                "Topsoil loss of {soil_loss} tons per hectare annually.",
                "Reduced soil fertility requiring additional inputs.",
                "Decreased water retention capacity.",
                "Long-term productivity decline if not addressed."
            ],
            "Desertification": [
                "Progressive land degradation reducing usable farm area.",
                "Declining soil organic matter and fertility.",
                "Increased wind erosion and dust problems.",
                "Potential long-term loss of agricultural viability."
            ]
        }
        
        # Severity factors based on risk level
        severity_factors = {
            "MINIMAL": {"yield_loss": (5, 10), "cost": (50, 100), "days": (3, 7), "soil_loss": (1, 3)},
            "LOW": {"yield_loss": (10, 20), "cost": (100, 200), "days": (7, 14), "soil_loss": (3, 5)},
            "MEDIUM": {"yield_loss": (20, 35), "cost": (200, 350), "days": (14, 21), "soil_loss": (5, 10)},
            "HIGH": {"yield_loss": (35, 60), "cost": (350, 600), "days": (21, 30), "soil_loss": (10, 20)},
            "EXTREME": {"yield_loss": (60, 90), "cost": (600, 1000), "days": (30, 45), "soil_loss": (20, 40)}
        }
        
        # Get templates for this risk type
        templates = impact_templates.get(risk_type, ["Potential impact on agricultural productivity."])
        
        # Select 2-3 impact statements
        num_statements = min(len(templates), random.randint(2, 3))
        selected_templates = random.sample(templates, num_statements)
        
        # Get severity factors for this risk level
        factors = severity_factors.get(risk_level, severity_factors["MEDIUM"])
        
        # Format the templates with random values within the severity range
        formatted_statements = []
        for template in selected_templates:
            if "{yield_loss}" in template:
                template = template.replace("{yield_loss}", str(random.randint(*factors["yield_loss"])))
            if "{cost}" in template:
                template = template.replace("{cost}", str(random.randint(*factors["cost"])))
            if "{days}" in template:
                template = template.replace("{days}", str(random.randint(*factors["days"])))
            if "{soil_loss}" in template:
                template = template.replace("{soil_loss}", str(random.randint(*factors["soil_loss"])))
            
            formatted_statements.append(template)
        
        return " ".join(formatted_statements)
    
    def _generate_mitigation_measures(self, risk_type):
        """Generate mitigation measures based on risk type."""
        mitigation_measures = {
            "Drought": [
                "Implement drought-resistant crop varieties.",
                "Install efficient irrigation systems.",
                "Practice mulching to conserve soil moisture.",
                "Develop water harvesting structures.",
                "Adjust planting calendar to avoid peak dry seasons."
            ],
            "Flooding": [
                "Improve drainage systems.",
                "Create raised planting beds.",
                "Construct flood protection barriers.",
                "Plant flood-tolerant crop varieties.",
                "Develop early warning systems for flood events."
            ],
            "Extreme Heat": [
                "Use shade cloth or netting during peak heat periods.",
                "Implement heat-tolerant crop varieties.",
                "Adjust planting times to avoid extreme heat periods.",
                "Increase irrigation frequency during heat waves.",
                "Apply mulch to reduce soil temperature."
            ],
            "Pest Outbreak": [
                "Implement integrated pest management strategies.",
                "Use resistant crop varieties.",
                "Practice crop rotation to break pest cycles.",
                "Monitor fields regularly for early detection.",
                "Maintain beneficial insect habitats."
            ],
            "Erratic Rainfall": [
                "Diversify crop varieties with different water requirements.",
                "Implement water harvesting and storage systems.",
                "Use soil moisture conservation techniques.",
                "Install supplemental irrigation systems.",
                "Utilize seasonal weather forecasts for planning."
            ],
            "Soil Erosion": [
                "Implement contour farming practices.",
                "Maintain vegetative cover or cover crops.",
                "Construct terraces on sloped land.",
                "Practice minimum tillage techniques.",
                "Plant windbreaks and buffer strips."
            ],
            "Desertification": [
                "Implement agroforestry systems.",
                "Reduce grazing intensity and improve management.",
                "Establish perennial vegetation cover.",
                "Apply organic matter to improve soil structure.",
                "Construct windbreaks to reduce wind erosion."
            ]
        }
        
        # Get measures for this risk type
        measures = mitigation_measures.get(risk_type, ["Implement climate-smart agricultural practices."])
        
        # Select 2-4 measures
        num_measures = min(len(measures), random.randint(2, 4))
        selected_measures = random.sample(measures, num_measures)
        
        return " ".join(selected_measures)
    
    def scrape_all_data(self, output_dir="scraped_data"):
        """
        Scrape all types of data and save to JSON files.
        
        Args:
            output_dir (str): Directory to save output files
            
        Returns:
            dict: Summary of scraped data
        """
        print(f"Starting comprehensive data scraping process...")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Scrape weather data for all regions
        weather_data = {}
        for region in self.regions:
            region_key = f"{region['name']}, {region['country']}"
            weather_data[region_key] = self.fetch_weather_data(region['lat'], region['lon'])
        
        with open(os.path.join(output_dir, "weather_data.json"), "w") as f:
            json.dump(weather_data, f, indent=2)
        
        # Scrape NDVI data for all regions
        ndvi_data = {}
        for region in self.regions:
            region_key = f"{region['name']}, {region['country']}"
            ndvi_data[region_key] = self.fetch_ndvi_data(region['lat'], region['lon'])
        
        with open(os.path.join(output_dir, "ndvi_data.json"), "w") as f:
            json.dump(ndvi_data, f, indent=2)
        
        # Generate crop price data
        price_data = {}
        for crop in self.crops:
            crop_prices = {}
            for region in self.regions:
                region_key = f"{region['name']}, {region['country']}"
                crop_prices[region_key] = self.fetch_crop_prices(crop['name'], region['country'])
            price_data[crop['name']] = crop_prices
        
        with open(os.path.join(output_dir, "crop_prices.json"), "w") as f:
            json.dump(price_data, f, indent=2)
        
        # Generate loan data
        loan_data = self.generate_loan_data(100)
        with open(os.path.join(output_dir, "loan_data.json"), "w") as f:
            json.dump(loan_data, f, indent=2)
        
        # Generate credit scores
        credit_data = self.generate_credit_scores(50)
        with open(os.path.join(output_dir, "credit_scores.json"), "w") as f:
            json.dump(credit_data, f, indent=2)
        
        # Generate climate risks
        climate_risks = self.generate_climate_risks()
        with open(os.path.join(output_dir, "climate_risks.json"), "w") as f:
            json.dump(climate_risks, f, indent=2)
        
        print(f"Data scraping complete. Files saved to {output_dir}/")
        
        return {
            "weather_data": len(weather_data),
            "ndvi_data": len(ndvi_data),
            "crop_prices": len(price_data),
            "loan_records": len(loan_data),
            "credit_scores": len(credit_data),
            "climate_risks": len(climate_risks),
            "output_directory": output_dir
        }

# Example usage
if __name__ == "__main__":
    scraper = DataScraper()
    summary = scraper.scrape_all_data()
    print(f"Scraping summary: {summary}")
