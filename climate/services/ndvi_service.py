import os
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from ..models import SatelliteImagery, NDVIData
from django.conf import settings

class NDVIService:
    """
    Service for fetching and processing NDVI (Normalized Difference Vegetation Index) data
    from NASA MODIS satellite imagery.
    """
    
    def __init__(self):
        """
        Initialize the NDVI service with API credentials
        """
        self.api_key = os.environ.get('NASA_API_KEY', '')
        self.base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    def fetch_ndvi_data(self, latitude, longitude, start_date=None, end_date=None):
        """
        Fetch NDVI data from NASA API for a specific location and date range
        
        Args:
            latitude (float): Latitude coordinate
            longitude (float): Longitude coordinate
            start_date (datetime, optional): Start date for data retrieval
            end_date (datetime, optional): End date for data retrieval
            
        Returns:
            dict: Response containing NDVI data
        """
        # Default to last 30 days if no dates provided
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
            
        # Format dates for API request
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        
        # Prepare request parameters
        params = {
            "start": start_str,
            "end": end_str,
            "latitude": latitude,
            "longitude": longitude,
            "community": "AG",
            "parameters": "NDVI",
            "format": "JSON",
            "user": "agrifinance"
        }
        
        if self.api_key:
            params["api_key"] = self.api_key
            
        try:
            # Make API request
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching NDVI data: {e}")
            return None
    
    def process_ndvi_data(self, data):
        """
        Process raw NDVI data from API response
        
        Args:
            data (dict): Raw API response data
            
        Returns:
            pandas.DataFrame: Processed NDVI data frame
        """
        if not data or 'properties' not in data or 'parameter' not in data['properties']:
            return None
            
        try:
            # Extract NDVI values
            ndvi_values = data['properties']['parameter']['NDVI']
            
            # Convert to DataFrame
            df = pd.DataFrame(list(ndvi_values.items()), columns=['date', 'ndvi'])
            
            # Convert string dates to datetime
            df['date'] = pd.to_datetime(df['date'])
            
            # Sort by date
            df = df.sort_values('date')
            
            return df
        except (KeyError, ValueError) as e:
            print(f"Error processing NDVI data: {e}")
            return None
    
    def calculate_ndvi_statistics(self, ndvi_values):
        """
        Calculate statistics from NDVI values
        
        Args:
            ndvi_values (list): List of NDVI values
            
        Returns:
            dict: Dictionary containing NDVI statistics
        """
        if not ndvi_values or len(ndvi_values) == 0:
            return {
                'average': None,
                'min': None,
                'max': None,
                'std_dev': None
            }
            
        try:
            # Convert to numpy array for calculations
            ndvi_array = np.array(ndvi_values)
            
            # Remove any undefined values
            ndvi_array = ndvi_array[~np.isnan(ndvi_array)]
            
            if len(ndvi_array) == 0:
                return {
                    'average': None,
                    'min': None,
                    'max': None,
                    'std_dev': None
                }
            
            # Calculate statistics
            return {
                'average': float(np.mean(ndvi_array)),
                'min': float(np.min(ndvi_array)),
                'max': float(np.max(ndvi_array)),
                'std_dev': float(np.std(ndvi_array))
            }
        except Exception as e:
            print(f"Error calculating NDVI statistics: {e}")
            return {
                'average': None,
                'min': None,
                'max': None,
                'std_dev': None
            }
    
    def fetch_and_store_ndvi_data(self, farm):
        """
        Fetch NDVI data for a farm and store it in the database
        
        Args:
            farm (Farm): Farm object to fetch NDVI data for
            
        Returns:
            dict: Result information including success status
        """
        try:
            if not farm.location:
                return {
                    'success': False,
                    'message': 'Farm location not defined'
                }
                
            # Extract centroid as approximate farm location
            centroid = farm.location.centroid
            latitude = centroid.y
            longitude = centroid.x
            
            # Fetch NDVI data for last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            ndvi_data = self.fetch_ndvi_data(latitude, longitude, start_date, end_date)
            
            if not ndvi_data:
                return {
                    'success': False,
                    'message': 'Failed to fetch NDVI data from API'
                }
                
            # Process the data
            processed_data = self.process_ndvi_data(ndvi_data)
            
            if processed_data is None or processed_data.empty:
                return {
                    'success': False,
                    'message': 'No valid NDVI data found'
                }
                
            # Get the latest date data
            latest_row = processed_data.iloc[-1]
            latest_date = latest_row['date'].date()
            latest_ndvi = latest_row['ndvi']
            
            # Calculate statistics for the period
            all_ndvi_values = processed_data['ndvi'].tolist()
            stats = self.calculate_ndvi_statistics(all_ndvi_values)
            
            # Create or update satellite imagery record
            imagery, created = SatelliteImagery.objects.update_or_create(
                region=farm.farmer.region,
                date=latest_date,
                satellite='MODIS',
                imagery_type='NDVI',
                defaults={
                    'resolution': 250,  # MODIS NDVI resolution in meters
                    'url': 'https://power.larc.nasa.gov/',  # Base URL of data source
                }
            )
            
            # Create or update NDVI data record
            ndvi, created = NDVIData.objects.update_or_create(
                farm=farm,
                date=latest_date,
                source='NASA POWER',
                defaults={
                    'ndvi_average': stats['average'] if latest_ndvi is None else latest_ndvi,
                    'ndvi_min': stats['min'],
                    'ndvi_max': stats['max'],
                    'imagery': imagery
                }
            )
            
            return {
                'success': True,
                'message': 'NDVI data successfully updated',
                'date': latest_date,
                'ndvi_average': ndvi.ndvi_average,
                'ndvi_min': ndvi.ndvi_min,
                'ndvi_max': ndvi.ndvi_max
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    def get_historical_ndvi_trend(self, farm, months=12):
        """
        Get historical NDVI trend data for a farm
        
        Args:
            farm (Farm): Farm object
            months (int): Number of months of historical data to include
            
        Returns:
            dict: Historical NDVI trend data
        """
        try:
            # Get NDVI data for the specified period
            start_date = datetime.now() - timedelta(days=30*months)
            
            ndvi_data = NDVIData.objects.filter(
                farm=farm,
                date__gte=start_date.date()
            ).order_by('date')
            
            if not ndvi_data:
                return {
                    'success': False,
                    'message': 'No historical NDVI data available'
                }
            
            # Prepare data for trend analysis
            dates = [data.date for data in ndvi_data]
            values = [float(data.ndvi_average) for data in ndvi_data]
            
            # Calculate trend (simple linear regression)
            x = np.arange(len(values))
            if len(x) > 1:  # Need at least 2 points for regression
                z = np.polyfit(x, values, 1)
                slope = z[0]
                
                # Determine trend direction
                if slope > 0.01:
                    trend = 'IMPROVING'
                elif slope < -0.01:
                    trend = 'DECLINING'
                else:
                    trend = 'STABLE'
            else:
                trend = 'INSUFFICIENT_DATA'
            
            return {
                'success': True,
                'dates': [d.strftime('%Y-%m-%d') for d in dates],
                'values': values,
                'trend': trend,
                'average': np.mean(values) if values else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
