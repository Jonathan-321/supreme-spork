"""
Models package initialization.
Import all models here to make them available from the models package.
"""
from .base import Base
from .farmer import Farmer, FarmerType
from .farm import Farm, CropType
from .loan import Loan, LoanType, LoanStatus, Payment
from .climate import WeatherForecast, ClimateRiskAssessment, RiskLevel, WeatherCondition

# Export all models
__all__ = [
    'Base',
    'Farmer', 'FarmerType',
    'Farm', 'CropType',
    'Loan', 'LoanType', 'LoanStatus', 'Payment',
    'WeatherForecast', 'ClimateRiskAssessment', 'RiskLevel', 'WeatherCondition'
]
