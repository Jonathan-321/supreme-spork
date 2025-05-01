"""
Weather API routes for the AgriFinance mobile app.
Provides weather forecasts and climate risk assessments for farmers.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import random
import logging

from api.models import WeatherForecast, WeatherCondition, ClimateRiskAssessment, RiskLevel
from api.models import Farm
from api import db

# Configure logging
logger = logging.getLogger('agrifinance_api.weather')

# Create blueprint
weather_api = Blueprint('weather_api', __name__)

@weather_api.route('/forecast')
def get_weather_forecast():
    """
    Get weather forecast for a farm or location.
    
    Query parameters:
    - farm_id: ID of the farm (optional)
    - latitude: Latitude coordinate (required if farm_id not provided)
    - longitude: Longitude coordinate (required if farm_id not provided)
    - days: Number of days to forecast (default: 5)
    """
    try:
        farm_id = request.args.get('farm_id', type=int)
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        days = request.args.get('days', default=5, type=int)
        
        # Validate input
        if farm_id:
            farm = db.session.get(Farm, farm_id)
            if not farm:
                return jsonify({"error": "Farm not found"}), 404
            
            latitude = farm.latitude
            longitude = farm.longitude
            location = farm.location
        elif latitude and longitude:
            location = f"Location ({latitude:.4f}, {longitude:.4f})"
        else:
            return jsonify({"error": "Either farm_id or latitude/longitude must be provided"}), 400
        
        # Check if we have recent forecasts in the database
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        existing_forecasts = db.session.query(WeatherForecast).filter(
            WeatherForecast.latitude.between(latitude - 0.01, latitude + 0.01),
            WeatherForecast.longitude.between(longitude - 0.01, longitude + 0.01),
            WeatherForecast.forecast_date >= today,
            WeatherForecast.forecast_date < today + timedelta(days=days)
        ).all()
        
        # If we have recent forecasts, return them
        if existing_forecasts and len(existing_forecasts) >= days:
            forecasts = sorted(existing_forecasts, key=lambda f: f.forecast_date)[:days]
            return jsonify({
                "location": location,
                "coordinates": {"latitude": latitude, "longitude": longitude},
                "forecasts": [forecast.to_dict() for forecast in forecasts]
            })
        
        # Otherwise, generate new forecasts
        # In a real app, this would call a weather API
        # For demo purposes, we'll generate realistic mock data
        forecasts = []
        
        # Weather conditions common in Ghana and Kenya
        conditions = [
            {"condition": WeatherCondition.SUNNY, "temp_range": (24, 34), "precip": (0, 0.1)},
            {"condition": WeatherCondition.PARTLY_CLOUDY, "temp_range": (22, 32), "precip": (0.1, 0.3)},
            {"condition": WeatherCondition.CLOUDY, "temp_range": (21, 30), "precip": (0.2, 0.4)},
            {"condition": WeatherCondition.LIGHT_RAIN, "temp_range": (20, 28), "precip": (0.5, 0.7)},
            {"condition": WeatherCondition.HEAVY_RAIN, "temp_range": (19, 26), "precip": (0.8, 1.0)},
            {"condition": WeatherCondition.THUNDERSTORM, "temp_range": (18, 25), "precip": (0.9, 1.0)}
        ]
        
        # Generate a realistic pattern
        # This is simplified, but could be made more realistic with Markov chains
        pattern = [
            random.choice(conditions[:2]),  # Mostly good weather today
            random.choice(conditions[:3]),  # Slight chance of clouds
            random.choice(conditions[1:4]),  # Higher chance of clouds/light rain
            random.choice(conditions),      # Any condition possible
            random.choice(conditions[:3])   # Return to better weather
        ]
        
        # Extend pattern if more days requested
        while len(pattern) < days:
            pattern.append(random.choice(conditions))
        
        # Create forecast objects
        for i in range(days):
            day = today + timedelta(days=i)
            weather_info = pattern[i]
            
            # Generate realistic temperatures
            temp_low = round(random.uniform(*weather_info["temp_range"]) - random.uniform(2, 4), 1)
            temp_high = round(random.uniform(*weather_info["temp_range"]), 1)
            
            # Generate precipitation data
            precip_chance = round(random.uniform(*weather_info["precip"]), 2)
            precip_amount = round(random.uniform(0, 30) * precip_chance, 1) if precip_chance > 0.3 else 0
            
            # Generate farming recommendations based on weather
            recommendation = generate_farming_recommendation(
                weather_info["condition"], 
                temp_high, 
                precip_chance
            )
            
            # Create forecast object
            forecast = WeatherForecast(
                location=location,
                latitude=latitude,
                longitude=longitude,
                forecast_date=day,
                condition=weather_info["condition"],
                temperature_high=temp_high,
                temperature_low=temp_low,
                precipitation_chance=precip_chance,
                precipitation_amount=precip_amount,
                humidity=round(random.uniform(60, 90), 1),
                wind_speed=round(random.uniform(5, 20), 1),
                farming_recommendation=recommendation
            )
            
            db.session.add(forecast)
            forecasts.append(forecast)
        
        db.session.commit()
        
        return jsonify({
            "location": location,
            "coordinates": {"latitude": latitude, "longitude": longitude},
            "forecasts": [forecast.to_dict() for forecast in forecasts]
        })
        
    except Exception as e:
        logger.error(f"Error getting weather forecast: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@weather_api.route('/climate-risk')
def get_climate_risk():
    """
    Get climate risk assessment for a farm.
    
    Query parameters:
    - farm_id: ID of the farm (required)
    """
    try:
        farm_id = request.args.get('farm_id', type=int)
        
        if not farm_id:
            return jsonify({"error": "farm_id is required"}), 400
            
        farm = db.session.get(Farm, farm_id)
        if not farm:
            return jsonify({"error": "Farm not found"}), 404
        
        # Check if we have a recent risk assessment
        recent_assessment = db.session.query(ClimateRiskAssessment).filter(
            ClimateRiskAssessment.farm_id == farm_id,
            ClimateRiskAssessment.assessment_date >= datetime.utcnow() - timedelta(days=30)
        ).order_by(ClimateRiskAssessment.assessment_date.desc()).first()
        
        if recent_assessment:
            return jsonify(recent_assessment.to_dict())
        
        # Otherwise, generate a new assessment
        # In a real app, this would use AI models and satellite data
        # For demo purposes, we'll generate realistic mock data
        
        # Base risk on farm location and crop type
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
        
        crop_factor = crop_risk_factors.get(farm.primary_crop.value, 1.0)
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
        mitigation_strategies = generate_mitigation_strategies(
            farm.primary_crop.value, 
            drought_risk, 
            flood_risk, 
            pest_risk
        )
        
        # Create assessment object
        assessment = ClimateRiskAssessment(
            farm_id=farm_id,
            risk_level=risk_level,
            risk_score=risk_score,
            drought_risk=drought_risk,
            flood_risk=flood_risk,
            pest_risk=pest_risk,
            mitigation_strategies=mitigation_strategies
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        return jsonify(assessment.to_dict())
        
    except Exception as e:
        logger.error(f"Error getting climate risk: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def generate_farming_recommendation(condition, temp_high, precip_chance):
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

def generate_mitigation_strategies(crop_type, drought_risk, flood_risk, pest_risk):
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
