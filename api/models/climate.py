"""
Climate and weather models for the AgriFinance API.
Focused on essential data needed for mobile-first approach with climate risk integration.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import Base

class RiskLevel(enum.Enum):
    """Climate risk levels for farms and regions"""
    MINIMAL = "Minimal"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    EXTREME = "Extreme"

class WeatherCondition(enum.Enum):
    """Common weather conditions"""
    SUNNY = "Sunny"
    PARTLY_CLOUDY = "Partly Cloudy"
    CLOUDY = "Cloudy"
    LIGHT_RAIN = "Light Rain"
    HEAVY_RAIN = "Heavy Rain"
    THUNDERSTORM = "Thunderstorm"
    DROUGHT = "Drought"

class WeatherForecast(Base):
    """
    Weather forecast model for farm locations.
    Designed for offline access in the mobile app.
    """
    __tablename__ = "weather_forecasts"
    
    id = Column(Integer, primary_key=True)
    location = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    forecast_date = Column(DateTime, nullable=False)  # Date the forecast is for
    created_at = Column(DateTime, default=datetime.utcnow)  # When the forecast was generated
    
    condition = Column(Enum(WeatherCondition), nullable=False)
    temperature_high = Column(Float, nullable=False)  # in Celsius
    temperature_low = Column(Float, nullable=False)  # in Celsius
    precipitation_chance = Column(Float, nullable=False)  # 0-1 probability
    precipitation_amount = Column(Float, nullable=True)  # in mm
    humidity = Column(Float, nullable=False)  # percentage
    wind_speed = Column(Float, nullable=False)  # in km/h
    
    # For farming recommendations
    farming_recommendation = Column(String(500), nullable=True)
    
    def to_dict(self):
        """Convert forecast to dictionary for API responses"""
        return {
            "id": self.id,
            "location": self.location,
            "coordinates": {
                "latitude": self.latitude,
                "longitude": self.longitude
            },
            "forecast_date": self.forecast_date.isoformat() if self.forecast_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "weather": {
                "condition": self.condition.value if self.condition else None,
                "temperature": {
                    "high": self.temperature_high,
                    "low": self.temperature_low
                },
                "precipitation": {
                    "chance": self.precipitation_chance,
                    "amount": self.precipitation_amount
                },
                "humidity": self.humidity,
                "wind_speed": self.wind_speed
            },
            "farming_recommendation": self.farming_recommendation
        }

class ClimateRiskAssessment(Base):
    """
    Climate risk assessment model for farms.
    Used for AI-driven loan adjustments based on climate conditions.
    """
    __tablename__ = "climate_risk_assessments"
    
    id = Column(Integer, primary_key=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    assessment_date = Column(DateTime, default=datetime.utcnow)
    
    risk_level = Column(Enum(RiskLevel), nullable=False)
    risk_score = Column(Float, nullable=False)  # 0-100 score
    
    # Specific risk factors
    drought_risk = Column(Float, nullable=False)  # 0-1 probability
    flood_risk = Column(Float, nullable=False)  # 0-1 probability
    pest_risk = Column(Float, nullable=False)  # 0-1 probability
    
    # AI-generated recommendations
    mitigation_strategies = Column(JSON, nullable=True)  # List of strategies
    
    def to_dict(self):
        """Convert risk assessment to dictionary for API responses"""
        return {
            "id": self.id,
            "farm_id": self.farm_id,
            "assessment_date": self.assessment_date.isoformat() if self.assessment_date else None,
            "risk_level": self.risk_level.value if self.risk_level else None,
            "risk_score": self.risk_score,
            "risk_factors": {
                "drought": self.drought_risk,
                "flood": self.flood_risk,
                "pest": self.pest_risk
            },
            "mitigation_strategies": self.mitigation_strategies
        }
