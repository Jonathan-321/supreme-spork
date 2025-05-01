"""
Satellite imagery service for crop health monitoring.

This service provides access to satellite imagery data for farms,
including NDVI (Normalized Difference Vegetation Index) analysis
for crop health monitoring.
"""
import logging
import numpy as np
from datetime import datetime, timedelta
import requests
import os
from pathlib import Path
import json

# Configure logging
logger = logging.getLogger('agrifinance_api.services.satellite')

class SatelliteService:
    """
    Service for satellite imagery and NDVI analysis.
    
    In a production environment, this would integrate with actual satellite data providers
    like Sentinel-2 via ESA's API. For the MVP, we'll simulate satellite data
    with realistic patterns based on crop types and seasons.
    """
    
    def __init__(self):
        """Initialize the satellite service"""
        self.api_key = os.environ.get('SATELLITE_API_KEY')
        self.cache_path = Path(__file__).parent.parent.parent / 'cache' / 'satellite'
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_path, exist_ok=True)
    
    def get_ndvi_data(self, latitude, longitude, farm_id=None, crop_type=None, date=None):
        """
        Get NDVI data for a specific location.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            farm_id: Optional farm ID for caching
            crop_type: Optional crop type for more realistic simulation
            date: Optional date for historical data (default: latest available)
            
        Returns:
            Dictionary with NDVI data
        """
        # Check cache first if farm_id is provided
        if farm_id:
            cached_data = self._check_cache(farm_id, date)
            if cached_data:
                return cached_data
        
        # In a real implementation, we would call a satellite data API here
        # For the MVP, we'll generate realistic simulated data
        ndvi_data = self._generate_simulated_ndvi(latitude, longitude, crop_type, date)
        
        # Cache the data if farm_id is provided
        if farm_id:
            self._cache_data(farm_id, ndvi_data)
        
        return ndvi_data
    
    def get_ndvi_time_series(self, latitude, longitude, farm_id=None, crop_type=None, start_date=None, end_date=None):
        """
        Get NDVI time series data for a specific location.
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            farm_id: Optional farm ID for caching
            crop_type: Optional crop type for more realistic simulation
            start_date: Start date for time series (default: 6 months ago)
            end_date: End date for time series (default: today)
            
        Returns:
            List of dictionaries with NDVI data over time
        """
        # Set default dates if not provided
        if not end_date:
            end_date = datetime.utcnow()
        elif isinstance(end_date, str):
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
        if not start_date:
            start_date = end_date - timedelta(days=180)  # Default to 6 months
        elif isinstance(start_date, str):
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        
        # Check cache first if farm_id is provided
        if farm_id:
            cached_series = self._check_cache_series(farm_id, start_date, end_date)
            if cached_series:
                return cached_series
        
        # Generate time series data
        # In a real app, we would fetch this from a satellite data provider
        time_series = []
        
        # Generate monthly data points
        current_date = start_date
        while current_date <= end_date:
            ndvi_data = self._generate_simulated_ndvi(
                latitude, 
                longitude, 
                crop_type, 
                current_date
            )
            time_series.append(ndvi_data)
            current_date += timedelta(days=30)  # Approximately monthly
        
        # Cache the data if farm_id is provided
        if farm_id:
            self._cache_time_series(farm_id, time_series)
        
        return time_series
    
    def _check_cache(self, farm_id, date=None):
        """Check if we have cached NDVI data for this farm"""
        try:
            cache_file = self.cache_path / f"farm_{farm_id}_ndvi.json"
            if not os.path.exists(cache_file):
                return None
                
            with open(cache_file, 'r') as f:
                data = json.load(f)
                
            # If date is specified, check if the cached data is for that date
            if date:
                date_str = date.isoformat() if isinstance(date, datetime) else date
                if data.get('date') != date_str:
                    return None
                    
            # Check if cache is recent (within 7 days)
            cache_date = datetime.fromisoformat(data.get('date').replace('Z', '+00:00'))
            if datetime.utcnow() - cache_date > timedelta(days=7):
                return None
                
            return data
        except Exception as e:
            logger.warning(f"Error reading cache for farm {farm_id}: {str(e)}")
            return None
    
    def _check_cache_series(self, farm_id, start_date, end_date):
        """Check if we have cached NDVI time series data for this farm"""
        try:
            cache_file = self.cache_path / f"farm_{farm_id}_ndvi_series.json"
            if not os.path.exists(cache_file):
                return None
                
            with open(cache_file, 'r') as f:
                data = json.load(f)
                
            # Check if cache covers the requested date range
            cache_start = datetime.fromisoformat(data[0].get('date').replace('Z', '+00:00'))
            cache_end = datetime.fromisoformat(data[-1].get('date').replace('Z', '+00:00'))
            
            if cache_start <= start_date and cache_end >= end_date:
                # Filter to requested date range
                filtered_data = [
                    d for d in data 
                    if datetime.fromisoformat(d.get('date').replace('Z', '+00:00')) >= start_date
                    and datetime.fromisoformat(d.get('date').replace('Z', '+00:00')) <= end_date
                ]
                return filtered_data
                
            return None
        except Exception as e:
            logger.warning(f"Error reading cache series for farm {farm_id}: {str(e)}")
            return None
    
    def _cache_data(self, farm_id, data):
        """Cache NDVI data for a farm"""
        try:
            cache_file = self.cache_path / f"farm_{farm_id}_ndvi.json"
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Error caching data for farm {farm_id}: {str(e)}")
    
    def _cache_time_series(self, farm_id, data):
        """Cache NDVI time series data for a farm"""
        try:
            cache_file = self.cache_path / f"farm_{farm_id}_ndvi_series.json"
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.warning(f"Error caching time series for farm {farm_id}: {str(e)}")
    
    def _generate_simulated_ndvi(self, latitude, longitude, crop_type=None, date=None):
        """
        Generate simulated NDVI data with realistic patterns.
        
        This mimics what real satellite data would look like, with variations
        based on crop type, season, and location.
        """
        # Use current date if not specified
        if not date:
            date = datetime.utcnow()
        elif isinstance(date, str):
            date = datetime.fromisoformat(date.replace('Z', '+00:00'))
        
        # Base NDVI value (healthy vegetation is typically 0.6-0.8)
        base_ndvi = 0.7
        
        # Adjust based on crop type
        crop_factors = {
            "Maize": 0.9,
            "Rice": 1.1,
            "Cassava": 0.85,
            "Yam": 0.8,
            "Cocoa": 1.0,
            "Coffee": 1.0,
            "Tea": 0.95,
            "Vegetables": 0.75,
            "Fruits": 0.9,
            "Other": 0.85
        }
        
        crop_factor = crop_factors.get(crop_type, 1.0) if crop_type else 1.0
        
        # Adjust based on season (simplified for Ghana/Kenya)
        # Assuming main growing season is April-October
        month = date.month
        if 4 <= month <= 10:
            # Growing season
            season_factor = 1.0 + 0.2 * np.sin((month - 4) * np.pi / 6)  # Peak in July
        else:
            # Dry season
            season_factor = 0.7
        
        # Add some randomness based on location
        # This creates spatial variation that would be seen in real satellite imagery
        location_seed = int(abs(latitude * 1000) + abs(longitude * 1000))
        np.random.seed(location_seed)
        location_factor = np.random.uniform(0.9, 1.1)
        
        # Add some randomness for natural variation
        random_factor = np.random.uniform(0.9, 1.1)
        
        # Calculate final NDVI value
        ndvi_value = base_ndvi * crop_factor * season_factor * location_factor * random_factor
        
        # Clamp to realistic range (-1 to 1, but typically 0 to 0.9 for vegetation)
        ndvi_value = max(-1.0, min(1.0, ndvi_value))
        
        # Generate pixel data (simplified representation of what would be an actual image)
        # In a real app, this would be an actual satellite image
        pixel_size = 0.01  # degrees (approximately 1km)
        grid_size = 5  # 5x5 grid
        
        pixels = []
        for i in range(grid_size):
            row = []
            for j in range(grid_size):
                # Add spatial variation to pixels
                pixel_variation = np.random.uniform(0.9, 1.1)
                pixel_value = max(-1.0, min(1.0, ndvi_value * pixel_variation))
                row.append(round(pixel_value, 2))
            pixels.append(row)
        
        # Calculate health status
        health_status = self._calculate_health_status(ndvi_value)
        
        # Generate farming recommendations based on NDVI
        recommendations = self._generate_recommendations(ndvi_value, crop_type, date)
        
        return {
            "farm_id": None,  # Will be set by caller if needed
            "latitude": latitude,
            "longitude": longitude,
            "date": date.isoformat(),
            "ndvi_value": round(ndvi_value, 2),
            "health_status": health_status,
            "pixel_data": pixels,
            "pixel_size_degrees": pixel_size,
            "recommendations": recommendations
        }
    
    def _calculate_health_status(self, ndvi_value):
        """Calculate crop health status based on NDVI value"""
        if ndvi_value >= 0.7:
            return "Excellent"
        elif ndvi_value >= 0.5:
            return "Good"
        elif ndvi_value >= 0.3:
            return "Fair"
        else:
            return "Poor"
    
    def _generate_recommendations(self, ndvi_value, crop_type, date):
        """Generate farming recommendations based on NDVI value and crop type"""
        recommendations = []
        
        # General recommendations based on NDVI
        if ndvi_value < 0.3:
            recommendations.append("Urgent attention needed: Crop health is poor")
            recommendations.append("Check for pest infestations or disease")
            recommendations.append("Consider soil testing for nutrient deficiencies")
            
        elif ndvi_value < 0.5:
            recommendations.append("Crop health is fair but needs improvement")
            recommendations.append("Review irrigation practices")
            recommendations.append("Consider applying appropriate fertilizers")
            
        elif ndvi_value < 0.7:
            recommendations.append("Crop health is good")
            recommendations.append("Continue current management practices")
            recommendations.append("Monitor for any changes in crop condition")
            
        else:
            recommendations.append("Crop health is excellent")
            recommendations.append("Maintain current practices")
            recommendations.append("Consider documenting successful techniques for future reference")
        
        # Add crop-specific recommendations if crop type is provided
        if crop_type:
            if crop_type == "Maize":
                if ndvi_value < 0.5:
                    recommendations.append("For maize: Check for nitrogen deficiency")
                    recommendations.append("Consider side-dressing with nitrogen fertilizer")
                
            elif crop_type == "Rice":
                if ndvi_value < 0.5:
                    recommendations.append("For rice: Check water levels in paddies")
                    recommendations.append("Monitor for rice blast disease")
                
            elif crop_type in ["Cocoa", "Coffee"]:
                if ndvi_value < 0.5:
                    recommendations.append(f"For {crop_type.lower()}: Check for shade management")
                    recommendations.append("Monitor for fungal diseases common in tree crops")
        
        # Add seasonal recommendations
        month = date.month
        if 4 <= month <= 5:  # Early growing season in Ghana/Kenya
            recommendations.append("Early season: Ensure proper plant spacing")
            recommendations.append("Monitor for early-season pests")
            
        elif 6 <= month <= 8:  # Mid growing season
            recommendations.append("Mid season: Monitor for signs of nutrient stress")
            recommendations.append("Ensure adequate water during critical growth stages")
            
        elif 9 <= month <= 10:  # Late growing season
            recommendations.append("Late season: Prepare for harvest")
            recommendations.append("Monitor for mature crop indicators")
        
        return recommendations

# Create a singleton instance
satellite_service = SatelliteService()
