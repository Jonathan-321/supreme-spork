"""
Farmer models for the AgriFinance API.
Focused on essential data needed for mobile-first approach.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from .base import Base

class FarmerType(enum.Enum):
    """Types of farmers in the system"""
    INDIVIDUAL = "Individual"
    COOPERATIVE = "Cooperative"
    SMALL_ENTERPRISE = "Small Enterprise"

class Farmer(Base):
    """
    Core farmer model with essential information.
    Simplified for mobile-first approach.
    """
    __tablename__ = "farmers"
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False, unique=True)
    farmer_type = Column(Enum(FarmerType), default=FarmerType.INDIVIDUAL)
    location = Column(String(200), nullable=False)  # Simplified location for MVP
    latitude = Column(Float, nullable=True)  # For geospatial features
    longitude = Column(Float, nullable=True)  # For geospatial features
    registration_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    farms = relationship("Farm", back_populates="farmer", cascade="all, delete-orphan")
    loans = relationship("Loan", back_populates="farmer", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert farmer to dictionary for API responses"""
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "farmer_type": self.farmer_type.value if self.farmer_type else None,
            "location": self.location,
            "coordinates": {
                "latitude": self.latitude,
                "longitude": self.longitude
            } if self.latitude and self.longitude else None,
            "registration_date": self.registration_date.isoformat() if self.registration_date else None,
            "farm_count": len(self.farms) if self.farms else 0,
            "active_loans": sum(1 for loan in self.loans if loan.is_active()) if self.loans else 0
        }
