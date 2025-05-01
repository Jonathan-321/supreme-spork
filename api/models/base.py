"""
Base models for the AgriFinance API.
These models are designed to be lightweight and focused on essential data needed for the mobile app.
"""
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

class Base(DeclarativeBase):
    """Base class for all models"""
    pass
