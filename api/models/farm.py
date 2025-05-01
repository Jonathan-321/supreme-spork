"""
Farm models for the AgriFinance API.
Focused on essential data needed for mobile-first approach with AI integration.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import Base

class CropType(enum.Enum):
    """Common crop types in Ghana and Kenya"""
    MAIZE = "Maize"
    RICE = "Rice"
    CASSAVA = "Cassava"
    YAM = "Yam"
    COCOA = "Cocoa"
    COFFEE = "Coffee"
    TEA = "Tea"
    VEGETABLES = "Vegetables"
    FRUITS = "Fruits"
    OTHER = "Other"

class Farm(Base):
    """
    Farm model with essential information for crop monitoring and AI analysis.
    """
    __tablename__ = "farms"
    
    id = Column(Integer, primary_key=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    name = Column(String(100), nullable=False)
    size_hectares = Column(Float, nullable=False)
    primary_crop = Column(Enum(CropType), nullable=False)
    secondary_crop = Column(Enum(CropType), nullable=True)
    location = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=True)  # For satellite imagery and weather data
    longitude = Column(Float, nullable=True)  # For satellite imagery and weather data
    registration_date = Column(DateTime, default=datetime.utcnow)
    
    # For AI crop health monitoring
    last_ndvi_value = Column(Float, nullable=True)  # Normalized Difference Vegetation Index
    last_ndvi_date = Column(DateTime, nullable=True)
    
    # Relationships
    farmer = relationship("Farmer", back_populates="farms")
    
    def to_dict(self):
        """Convert farm to dictionary for API responses"""
        return {
            "id": self.id,
            "farmer_id": self.farmer_id,
            "name": self.name,
            "size_hectares": self.size_hectares,
            "primary_crop": self.primary_crop.value if self.primary_crop else None,
            "secondary_crop": self.secondary_crop.value if self.secondary_crop else None,
            "location": self.location,
            "coordinates": {
                "latitude": self.latitude,
                "longitude": self.longitude
            } if self.latitude and self.longitude else None,
            "registration_date": self.registration_date.isoformat() if self.registration_date else None,
            "crop_health": {
                "ndvi_value": self.last_ndvi_value,
                "ndvi_date": self.last_ndvi_date.isoformat() if self.last_ndvi_date else None,
                "health_status": self._calculate_health_status()
            } if self.last_ndvi_value is not None else None
        }
    
    def _calculate_health_status(self):
        """Calculate health status based on NDVI value"""
        if self.last_ndvi_value is None:
            return None
        
        if self.last_ndvi_value >= 0.7:
            return "Excellent"
        elif self.last_ndvi_value >= 0.5:
            return "Good"
        elif self.last_ndvi_value >= 0.3:
            return "Fair"
        else:
            return "Poor"
