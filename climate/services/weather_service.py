import os
import requests
import numpy as np
from datetime import datetime, timedelta
from django.utils import timezone
from ..models import WeatherData, WeatherForecast

class WeatherService:
    """
    Service for fetching and processing weather data from external APIs
    """
    
    def __init__(self):
        """
        Initialize the weather service with API credentials
        """
        self.api_key = os.environ.get('OPENWEATHER_API_KEY', '')
        self.base_url = "https://api.openweathermap.org/data/2.5"
    
    def fetch_current_weather(self, latitude, longitude):
        """
        Fetch current weather data for a specific location
        
        Args:
            latitude (float): Latitude coordinate
            longitude (float): Longitude coordinate
            
        Returns:
            dict: Weather data response
        """
        url = f"{self.base_url}/weather"
        
        params = {
            'lat': latitude,
            'lon': longitude,
            'units': 'metric',  # Use metric units (Celsius, mm, etc.)
            'appid': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching current weather: {e}")
            return None
    
    def fetch_weather_forecast(self, latitude, longitude, days=7):
        """
        Fetch weather forecast for a specific location
        
        Args:
            latitude (float): Latitude coordinate
            longitude (float): Longitude coordinate
            days (int): Number of days to forecast (max 7 for free tier)
            
        Returns:
            dict: Weather forecast response
        """
        # Use OneCall API for forecast
        url = f"{self.base_url}/onecall"
        
        params = {
            'lat': latitude,
            'lon': longitude,
            'exclude': 'minutely,hourly,alerts',  # Exclude unnecessary data
            'units': 'metric',
            'appid': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Limit to requested number of days
            if 'daily' in data:
                data['daily'] = data['daily'][:min(days, len(data['daily']))]
                
            return data
        except requests.RequestException as e:
            print(f"Error fetching weather forecast: {e}")
            return None
    
    def fetch_historical_weather(self, latitude, longitude, days=30):
        """
        Fetch historical weather data for a specific location
        
        Args:
            latitude (float): Latitude coordinate
            longitude (float): Longitude coordinate
            days (int): Number of past days to fetch
            
        Returns:
            list: List of daily historical weather data
        """
        # Use OpenWeatherMap historical data API
        url = f"{self.base_url}/onecall/timemachine"
        
        # Can only fetch one day at a time with free tier
        # So we'll need to make multiple requests
        historical_data = []
        
        # Get data for each day
        for day in range(days):
            # Calculate timestamp for past day (in seconds)
            dt = int((datetime.now() - timedelta(days=day)).timestamp())
            
            params = {
                'lat': latitude,
                'lon': longitude,
                'dt': dt,
                'units': 'metric',
                'appid': self.api_key
            }
            
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                day_data = response.json()
                
                if 'current' in day_data:
                    historical_data.append(day_data)
                
            except requests.RequestException as e:
                print(f"Error fetching historical weather for day {day}: {e}")
                continue
                
        return historical_data
    
    def process_daily_weather(self, weather_data):
        """
        Process raw weather data into a standardized format
        
        Args:
            weather_data (dict): Raw weather data from API
            
        Returns:
            dict: Processed weather data
        """
        if not weather_data:
            return None
            
        try:
            # Extract relevant fields
            processed = {
                'temperature': {
                    'current': weather_data.get('main', {}).get('temp'),
                    'min': weather_data.get('main', {}).get('temp_min'),
                    'max': weather_data.get('main', {}).get('temp_max'),
                    'feels_like': weather_data.get('main', {}).get('feels_like')
                },
                'humidity': weather_data.get('main', {}).get('humidity'),
                'pressure': weather_data.get('main', {}).get('pressure'),
                'wind': {
                    'speed': weather_data.get('wind', {}).get('speed'),
                    'direction': weather_data.get('wind', {}).get('deg')
                },
                'clouds': weather_data.get('clouds', {}).get('all'),
                'weather': {
                    'main': weather_data.get('weather', [{}])[0].get('main'),
                    'description': weather_data.get('weather', [{}])[0].get('description'),
                    'icon': weather_data.get('weather', [{}])[0].get('icon')
                },
                'rain': weather_data.get('rain', {}).get('1h', 0),
                'datetime': datetime.fromtimestamp(weather_data.get('dt', 0))
            }
            
            return processed
        except (KeyError, IndexError) as e:
            print(f"Error processing weather data: {e}")
            return None
    
    def store_weather_data(self, region, weather_data, source='OpenWeatherMap'):
        """
        Store weather data in the database
        
        Args:
            region (Region): Region object
            weather_data (dict): Processed weather data
            source (str): Data source identifier
            
        Returns:
            WeatherData: Saved weather data object
        """
        if not weather_data:
            return None
            
        try:
            # Create or update weather data record
            data_date = weather_data['datetime'].date()
            
            weather_record, created = WeatherData.objects.update_or_create(
                region=region,
                date=data_date,
                source=source,
                defaults={
                    'temperature_max': weather_data['temperature']['max'],
                    'temperature_min': weather_data['temperature']['min'],
                    'temperature_avg': weather_data['temperature']['current'],
                    'precipitation': weather_data['rain'],
                    'humidity': weather_data['humidity'],
                    'wind_speed': weather_data['wind']['speed']
                }
            )
            
            return weather_record
        except Exception as e:
            print(f"Error storing weather data: {e}")
            return None
    
    def store_weather_forecast(self, region, forecast_data, source='OpenWeatherMap'):
        """
        Store weather forecast in the database
        
        Args:
            region (Region): Region object
            forecast_data (dict): Weather forecast data
            source (str): Data source identifier
            
        Returns:
            list: List of saved forecast objects
        """
        if not forecast_data or 'daily' not in forecast_data:
            return []
            
        saved_forecasts = []
        forecast_date = timezone.now().date()
        
        try:
            # Process each day in the forecast
            for day_data in forecast_data['daily']:
                # Convert timestamp to date
                prediction_date = datetime.fromtimestamp(day_data['dt']).date()
                
                # Extract values
                temp_max = day_data['temp']['max']
                temp_min = day_data['temp']['min']
                
                # Get precipitation probability and amount
                pop = day_data.get('pop', 0) * 100  # Convert from 0-1 to percentage
                rain = day_data.get('rain', 0)
                
                # Create or update forecast record
                forecast, created = WeatherForecast.objects.update_or_create(
                    region=region,
                    forecast_date=forecast_date,
                    prediction_date=prediction_date,
                    source=source,
                    defaults={
                        'temperature_max': temp_max,
                        'temperature_min': temp_min,
                        'precipitation_probability': pop,
                        'precipitation_amount': rain
                    }
                )
                
                saved_forecasts.append(forecast)
                
            return saved_forecasts
        except Exception as e:
            print(f"Error storing weather forecast: {e}")
            return []
    
    def get_weather_forecast(self, region, days=7):
        """
        Get weather forecast for a region
        
        Args:
            region (Region): Region object
            days (int): Number of days to forecast
            
        Returns:
            dict: Forecast data ready for display
        """
        try:
            # Check if we have recent forecast data in the database
            today = timezone.now().date()
            existing_forecast = WeatherForecast.objects.filter(
                region=region,
                forecast_date=today,
                prediction_date__gte=today
            ).order_by('prediction_date')
            
            # If we have enough forecast days, use the database data
            if existing_forecast.count() >= days:
                forecast_data = []
                
                for forecast in existing_forecast[:days]:
                    forecast_data.append({
                        'date': forecast.prediction_date.strftime('%Y-%m-%d'),
                        'day': forecast.prediction_date.strftime('%A'),
                        'temp_max': float(forecast.temperature_max),
                        'temp_min': float(forecast.temperature_min),
                        'precipitation_probability': float(forecast.precipitation_probability),
                        'precipitation_amount': float(forecast.precipitation_amount) if forecast.precipitation_amount else 0
                    })
                
                return forecast_data
            
            # Otherwise, fetch new data if we have coordinates
            if region.area and hasattr(region.area, 'centroid'):
                centroid = region.area.centroid
                latitude = centroid.y
                longitude = centroid.x
                
                # Fetch forecast from API
                api_forecast = self.fetch_weather_forecast(latitude, longitude, days)
                
                if api_forecast:
                    # Store the forecast data
                    self.store_weather_forecast(region, api_forecast)
                    
                    # Format the data for display
                    forecast_data = []
                    
                    for day_data in api_forecast['daily'][:days]:
                        date_obj = datetime.fromtimestamp(day_data['dt'])
                        forecast_data.append({
                            'date': date_obj.strftime('%Y-%m-%d'),
                            'day': date_obj.strftime('%A'),
                            'temp_max': day_data['temp']['max'],
                            'temp_min': day_data['temp']['min'],
                            'precipitation_probability': day_data.get('pop', 0) * 100,
                            'precipitation_amount': day_data.get('rain', 0)
                        })
                    
                    return forecast_data
            
            # If all else fails, return empty list
            return []
                
        except Exception as e:
            print(f"Error getting weather forecast: {e}")
            return []
    
    def calculate_seasonal_anomalies(self, region, start_date=None, end_date=None):
        """
        Calculate seasonal weather anomalies for a region
        
        Args:
            region (Region): Region object
            start_date (date, optional): Start date for analysis
            end_date (date, optional): End date for analysis
            
        Returns:
            dict: Seasonal anomaly data
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).date()
        if not end_date:
            end_date = datetime.now().date()
            
        try:
            # Get weather data for the specified period
            weather_data = WeatherData.objects.filter(
                region=region,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date')
            
            if not weather_data:
                return {
                    'success': False,
                    'message': 'Insufficient weather data for analysis'
                }
                
            # Extract temperature and precipitation values
            dates = [data.date for data in weather_data]
            temps = [float(data.temperature_avg) for data in weather_data if data.temperature_avg]
            precip = [float(data.precipitation) for data in weather_data if data.precipitation]
            
            # Calculate baselines (5-year climatology would be better, but using available data)
            avg_temp = np.mean(temps) if temps else None
            avg_precip = np.mean(precip) if precip else None
            
            # Calculate anomalies
            temp_anomalies = [t - avg_temp for t in temps] if avg_temp else []
            precip_anomalies = [p - avg_precip for p in precip] if avg_precip else []
            
            # Calculate recent anomalies (last 30 days)
            recent_start_idx = max(0, len(temp_anomalies) - 30)
            recent_temp_anomaly = np.mean(temp_anomalies[recent_start_idx:]) if temp_anomalies else None
            recent_precip_anomaly = np.mean(precip_anomalies[recent_start_idx:]) if precip_anomalies else None
            
            # Determine anomaly status
            temp_status = 'NORMAL'
            if recent_temp_anomaly is not None:
                if recent_temp_anomaly > 1.5:
                    temp_status = 'MUCH_WARMER'
                elif recent_temp_anomaly > 0.5:
                    temp_status = 'WARMER'
                elif recent_temp_anomaly < -1.5:
                    temp_status = 'MUCH_COOLER'
                elif recent_temp_anomaly < -0.5:
                    temp_status = 'COOLER'
            
            precip_status = 'NORMAL'
            if recent_precip_anomaly is not None:
                if recent_precip_anomaly > 5:
                    precip_status = 'MUCH_WETTER'
                elif recent_precip_anomaly > 2:
                    precip_status = 'WETTER'
                elif recent_precip_anomaly < -5:
                    precip_status = 'MUCH_DRIER'
                elif recent_precip_anomaly < -2:
                    precip_status = 'DRIER'
            
            return {
                'success': True,
                'temp_anomaly': recent_temp_anomaly,
                'precip_anomaly': recent_precip_anomaly,
                'temp_status': temp_status,
                'precip_status': precip_status,
                'baseline_temp': avg_temp,
                'baseline_precip': avg_precip
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error: {str(e)}'
            }
