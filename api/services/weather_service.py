"""
Weather service for the AgriFinance mobile app.

This service provides weather forecasts and climate risk assessments
with a focus on agricultural relevance and offline capabilities.
"""
import logging
import numpy as np
from datetime import datetime, timedelta
import requests
import os
from pathlib import Path
import json
import random

from api.models import WeatherCondition, RiskLevel

# Configure logging
logger = logging.getLogger('agrifinance_api.services.weather')

class WeatherService:
    """
    Service for weather forecasts and climate risk assessments.
    
    In a production environment, this would integrate with weather APIs
    like OpenWeatherMap, AccuWeather, or aWhere. For the MVP, we'll simulate
    weather data with realistic patterns for Ghana and Kenya.
    """
    
    def __init__(self):
        """Initialize the weather service"""
        self.api_key = os.environ.get('WEATHER_API_KEY')
        self.cache_path = Path(__file__).parent.parent.parent / 'cache' / 'weather'
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_path, exist_ok=True)
        
        # Weather conditions common in Ghana and Kenya
        self.conditions = [
            {"condition": WeatherCondition.SUNNY, "temp_range": (24, 34), "precip": (0, 0.1)},
            {"condition": WeatherCondition.PARTLY_CLOUDY, "temp_range": (22, 32), "precip": (0.1, 0.3)},
            {"condition": WeatherCondition.CLOUDY, "temp_range": (21, 30), "precip": (0.2, 0.4)},
            {"condition": WeatherCondition.LIGHT_RAIN, "temp_range": (20, 28), "precip": (0.5, 0.7)},
            {"condition": WeatherCondition.HEAVY_RAIN, "temp_range": (19, 26), "precip": (0.8, 1.0)},
            {"condition": WeatherCondition.THUNDERSTORM, "temp_range": (18, 25), "precip": (0.9, 1.0)}
        ]
    
    def get_weather_forecast(self, latitude, longitude, location_name=None, days=5):
        """
        Get weather forecast for a specific location.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            location_name: Optional location name for display
            days: Number of days to forecast (default: 5)
            
        Returns:
            Dictionary with weather forecast data
        """
        # Check cache first
        cached_forecast = self._check_cache(latitude, longitude)
        if cached_forecast and len(cached_forecast.get('forecasts', [])) >= days:
            # Return only the requested number of days
            cached_forecast['forecasts'] = cached_forecast['forecasts'][:days]
            return cached_forecast
        
        # In a real implementation, we would call a weather API here
        # For the MVP, we'll generate realistic simulated data
        location = location_name or f"Location ({latitude:.4f}, {longitude:.4f})"
        forecast = self._generate_simulated_forecast(latitude, longitude, location, days)
        
        # Cache the forecast
        self._cache_forecast(latitude, longitude, forecast)
        
        return forecast
    
    def get_climate_risk(self, latitude, longitude, crop_type=None):
        """
        Get climate risk assessment for a specific location.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            crop_type: Optional crop type for more accurate risk assessment
            
        Returns:
            Dictionary with climate risk data
        """
        # Base risk on location
        # This would be much more sophisticated in a real app
        base_risk = random.uniform(0.2, 0.8)
        
        # Adjust for crop type
        crop_risk_factors = {
            "Maize": 1.0,
            "Rice": 1.2,
            "Cassava": 0.8,
            "Yam": 0.9,
            "Cocoa": 1.1,
            "Coffee": 1.1,
            "Tea": 1.0,
            "Vegetables": 1.3,
            "Fruits": 1.2,
            "Other": 1.0
        }
        
        crop_factor = crop_risk_factors.get(crop_type, 1.0) if crop_type else 1.0
        adjusted_risk = base_risk * crop_factor
        
        # Calculate specific risks
        drought_risk = min(1.0, adjusted_risk * random.uniform(0.8, 1.2))
        flood_risk = min(1.0, adjusted_risk * random.uniform(0.8, 1.2))
        pest_risk = min(1.0, adjusted_risk * random.uniform(0.8, 1.2))
        
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
        
        # Generate mitigation strategies
        mitigation_strategies = self._generate_mitigation_strategies(
            crop_type, 
            drought_risk, 
            flood_risk, 
            pest_risk
        )
        
        return {
            "latitude": latitude,
            "longitude": longitude,
            "crop_type": crop_type,
            "risk_level": risk_level.value,
            "risk_score": risk_score,
            "drought_risk": round(drought_risk, 2),
            "flood_risk": round(flood_risk, 2),
            "pest_risk": round(pest_risk, 2),
            "assessment_date": datetime.utcnow().isoformat(),
            "mitigation_strategies": mitigation_strategies
        }
    
    def _check_cache(self, latitude, longitude):
        """Check if we have cached forecast data for this location"""
        try:
            # Round coordinates to reduce cache fragmentation
            lat_rounded = round(latitude, 2)
            lon_rounded = round(longitude, 2)
            
            cache_file = self.cache_path / f"forecast_{lat_rounded}_{lon_rounded}.json"
            if not os.path.exists(cache_file):
                return None
                
            with open(cache_file, 'r') as f:
                data = json.load(f)
                
            # Check if cache is recent (within 6 hours)
            cache_date = datetime.fromisoformat(data.get('generated_at').replace('Z', '+00:00'))
            if datetime.utcnow() - cache_date > timedelta(hours=6):
                return None
                
            return data
        except Exception as e:
            logger.warning(f"Error reading weather cache for {latitude}, {longitude}: {str(e)}")
            return None
    
    def _cache_forecast(self, latitude, longitude, forecast):
        """Cache forecast data for a location"""
        try:
            # Round coordinates to reduce cache fragmentation
            lat_rounded = round(latitude, 2)
            lon_rounded = round(longitude, 2)
            
            cache_file = self.cache_path / f"forecast_{lat_rounded}_{lon_rounded}.json"
            with open(cache_file, 'w') as f:
                json.dump(forecast, f)
        except Exception as e:
            logger.warning(f"Error caching forecast for {latitude}, {longitude}: {str(e)}")
    
    def _generate_simulated_forecast(self, latitude, longitude, location, days):
        """
        Generate simulated weather forecast with realistic patterns.
        
        This mimics what real weather forecast data would look like, with
        day-to-day transitions that make meteorological sense.
        """
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        forecasts = []
        
        # Generate a realistic pattern
        # This is simplified, but could be made more realistic with Markov chains
        # Start with a random condition, weighted toward good weather
        current_condition_idx = np.random.choice(
            [0, 1, 2, 3, 4, 5],  # Indices into self.conditions
            p=[0.3, 0.3, 0.2, 0.1, 0.05, 0.05]  # Probabilities (higher for good weather)
        )
        
        # For each day in the forecast
        for i in range(days):
            day = today + timedelta(days=i)
            day_name = day.strftime("%a") if i > 0 else "Today"
            
            # Get the current condition
            weather_info = self.conditions[current_condition_idx]
            
            # Generate realistic temperatures
            temp_low = round(random.uniform(*weather_info["temp_range"]) - random.uniform(2, 4), 1)
            temp_high = round(random.uniform(*weather_info["temp_range"]), 1)
            
            # Generate precipitation data
            precip_chance = round(random.uniform(*weather_info["precip"]), 2)
            precip_amount = round(random.uniform(0, 30) * precip_chance, 1) if precip_chance > 0.3 else 0
            
            # Generate farming recommendations based on weather
            recommendation = self._generate_farming_recommendation(
                weather_info["condition"], 
                temp_high, 
                precip_chance
            )
            
            # Create forecast object
            forecast = {
                "date": day.isoformat(),
                "day_name": day_name,
                "condition": weather_info["condition"].value,
                "temperature": {
                    "high": temp_high,
                    "low": temp_low,
                    "unit": "C"
                },
                "precipitation": {
                    "chance": precip_chance,
                    "amount": precip_amount,
                    "unit": "mm"
                },
                "humidity": round(random.uniform(60, 90), 1),
                "wind_speed": round(random.uniform(5, 20), 1),
                "wind_unit": "km/h",
                "farming_recommendation": recommendation
            }
            
            forecasts.append(forecast)
            
            # Transition to next day's weather (weather tends to persist but can change)
            # This creates a more realistic sequence than purely random conditions
            transition_probs = self._get_transition_probabilities(current_condition_idx)
            current_condition_idx = np.random.choice(
                range(len(self.conditions)),
                p=transition_probs
            )
        
        return {
            "location": location,
            "coordinates": {
                "latitude": latitude,
                "longitude": longitude
            },
            "generated_at": datetime.utcnow().isoformat(),
            "forecasts": forecasts
        }
    
    def _get_transition_probabilities(self, current_idx):
        """
        Get probabilities for transitioning from current weather to next day's weather.
        Weather tends to persist but can change gradually.
        """
        # Number of possible conditions
        n = len(self.conditions)
        
        # Start with low probability for all transitions
        probs = [0.05] * n
        
        # Higher probability to stay the same
        probs[current_idx] = 0.4
        
        # Higher probabilities for adjacent conditions (gradual changes)
        for offset in [-1, 1]:
            idx = (current_idx + offset) % n
            probs[idx] = 0.2
        
        # Normalize to ensure sum is 1
        return [p / sum(probs) for p in probs]
    
    def _generate_farming_recommendation(self, condition, temp_high, precip_chance):
        """Generate farming recommendations based on weather conditions"""
        if condition == WeatherCondition.SUNNY and temp_high > 30:
            return "Water crops early morning or evening. Consider shade for sensitive seedlings."
        
        elif condition == WeatherCondition.SUNNY:
            return "Good day for field work, weeding, and harvesting mature crops."
        
        elif condition == WeatherCondition.PARTLY_CLOUDY:
            return "Ideal conditions for most field activities and planting new crops."
        
        elif condition == WeatherCondition.CLOUDY:
            return "Good day for transplanting seedlings and applying fertilizers."
        
        elif condition == WeatherCondition.LIGHT_RAIN and precip_chance > 0.6:
            return "Light rain expected. Hold off on applying pesticides or fertilizers."
        
        elif condition == WeatherCondition.LIGHT_RAIN:
            return "Light rain possible. Good conditions for planting or transplanting."
        
        elif condition == WeatherCondition.HEAVY_RAIN:
            return "Heavy rain expected. Check drainage systems and avoid field work."
        
        elif condition == WeatherCondition.THUNDERSTORM:
            return "Thunderstorms expected. Secure equipment and stay indoors during storms."
        
        return "Monitor weather conditions and adjust farm activities accordingly."
    
    def _generate_mitigation_strategies(self, crop_type, drought_risk, flood_risk, pest_risk):
        """Generate climate risk mitigation strategies based on risk factors"""
        strategies = []
        
        # Drought strategies
        if drought_risk > 0.6:
            strategies.append({
                "risk_type": "drought",
                "severity": "high",
                "strategies": [
                    "Implement water conservation techniques like mulching",
                    "Consider drought-resistant crop varieties for next season",
                    "Install water harvesting systems before dry season"
                ]
            })
        elif drought_risk > 0.3:
            strategies.append({
                "risk_type": "drought",
                "severity": "medium",
                "strategies": [
                    "Monitor soil moisture regularly",
                    "Apply mulch to reduce evaporation",
                    "Schedule irrigation during cooler parts of the day"
                ]
            })
        
        # Flood strategies
        if flood_risk > 0.6:
            strategies.append({
                "risk_type": "flood",
                "severity": "high",
                "strategies": [
                    "Improve drainage systems around fields",
                    "Consider raised beds for vulnerable crops",
                    "Plant cover crops to prevent soil erosion"
                ]
            })
        elif flood_risk > 0.3:
            strategies.append({
                "risk_type": "flood",
                "severity": "medium",
                "strategies": [
                    "Clear drainage channels of debris",
                    "Monitor weather forecasts for heavy rain events",
                    "Consider contour plowing to manage water flow"
                ]
            })
        
        # Pest strategies
        if pest_risk > 0.6:
            strategies.append({
                "risk_type": "pest",
                "severity": "high",
                "strategies": [
                    "Implement integrated pest management practices",
                    "Consider resistant varieties for next planting",
                    "Increase monitoring frequency for early detection"
                ]
            })
        elif pest_risk > 0.3:
            strategies.append({
                "risk_type": "pest",
                "severity": "medium",
                "strategies": [
                    "Monitor crops regularly for signs of pest damage",
                    "Maintain field hygiene to reduce pest habitats",
                    "Consider beneficial insects for natural control"
                ]
            })
        
        # Add crop-specific strategies
        if crop_type == "Maize":
            strategies.append({
                "risk_type": "crop_specific",
                "crop": "Maize",
                "strategies": [
                    "Consider staggered planting to spread risk",
                    "Monitor for fall armyworm during vegetative stages",
                    "Ensure adequate spacing for air circulation"
                ]
            })
        elif crop_type == "Rice":
            strategies.append({
                "risk_type": "crop_specific",
                "crop": "Rice",
                "strategies": [
                    "Maintain optimal water levels in paddies",
                    "Monitor for rice blast during humid conditions",
                    "Consider SRI (System of Rice Intensification) techniques"
                ]
            })
        
        return strategies

# Create a singleton instance
weather_service = WeatherService()
