from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ClimateRisk, NDVIData, WeatherData, WeatherForecast
from core.models import Farm, Region, Loan
from climate.services.ndvi_service import NDVIService
from climate.services.weather_service import WeatherService
from climate.services.climate_risk_service import ClimateRiskService
import json
from datetime import datetime, timedelta

@login_required
def climate_dashboard(request):
    """
    Climate dashboard showing climate risk and data for farmer's region
    """
    try:
        farmer = request.user.farmer
        region = farmer.region
        farms = Farm.objects.filter(farmer=farmer)
        
        # Get climate risks for the region
        climate_risks = ClimateRisk.objects.filter(
            region=region,
            valid_until__gte=datetime.now().date()
        ).order_by('risk_type')
        
        # Get recent weather data
        weather_data = WeatherData.objects.filter(
            region=region
        ).order_by('-date')[:30]  # Last 30 days
        
        # Get weather forecast
        weather_forecast = WeatherForecast.objects.filter(
            region=region,
            prediction_date__gte=datetime.now().date()
        ).order_by('prediction_date')[:10]  # Next 10 days
        
        # Process weather data for charts
        dates = [data.date.strftime('%Y-%m-%d') for data in weather_data]
        temperatures = [float(data.temperature_avg) for data in weather_data]
        precipitation = [float(data.precipitation) if data.precipitation else 0 for data in weather_data]
        
        # Get NDVI data for farms
        farm_ndvi_data = {}
        for farm in farms:
            ndvi_data = NDVIData.objects.filter(farm=farm).order_by('-date')[:12]  # Last 12 records
            if ndvi_data:
                farm_ndvi_data[farm.id] = {
                    'name': farm.name,
                    'dates': [data.date.strftime('%Y-%m-%d') for data in ndvi_data],
                    'values': [float(data.ndvi_average) for data in ndvi_data]
                }
        
        context = {
            'region': region,
            'climate_risks': climate_risks,
            'weather_dates': json.dumps(dates),
            'weather_temperatures': json.dumps(temperatures),
            'weather_precipitation': json.dumps(precipitation),
            'weather_forecast': weather_forecast,
            'farm_ndvi_data': json.dumps(farm_ndvi_data)
        }
        return render(request, 'climate/dashboard.html', context)
    except Exception as e:
        return render(request, 'climate/dashboard.html', {'error': str(e)})

@login_required
def farm_climate_data(request, farm_id):
    """
    View to show detailed climate data for a specific farm
    """
    farm = get_object_or_404(Farm, id=farm_id, farmer=request.user.farmer)
    region = request.user.farmer.region
    
    # Get NDVI data
    ndvi_data = NDVIData.objects.filter(farm=farm).order_by('-date')[:24]  # Last 24 records
    
    # Get weather data for the region
    weather_data = WeatherData.objects.filter(
        region=region
    ).order_by('-date')[:60]  # Last 60 days
    
    # Process data for charts
    ndvi_dates = [data.date.strftime('%Y-%m-%d') for data in ndvi_data]
    ndvi_values = [float(data.ndvi_average) for data in ndvi_data]
    
    weather_dates = [data.date.strftime('%Y-%m-%d') for data in weather_data]
    temperatures = [float(data.temperature_avg) if data.temperature_avg else None for data in weather_data]
    precipitation = [float(data.precipitation) if data.precipitation else 0 for data in weather_data]
    
    context = {
        'farm': farm,
        'ndvi_dates': json.dumps(ndvi_dates),
        'ndvi_values': json.dumps(ndvi_values),
        'weather_dates': json.dumps(weather_dates),
        'weather_temperatures': json.dumps(temperatures),
        'weather_precipitation': json.dumps(precipitation),
    }
    return render(request, 'climate/farm_data.html', context)

@login_required
def loan_climate_risk(request, loan_id):
    """
    View to show climate risk assessment for a specific loan
    """
    loan = get_object_or_404(Loan, loan_id=loan_id, farmer=request.user.farmer)
    
    # Get climate risk service
    risk_service = ClimateRiskService()
    
    # Perform risk assessment for the loan
    risk_assessment = risk_service.assess_loan_climate_risk(loan)
    
    # Get climate adjustments made to the loan
    climate_adjustments = loan.climate_adjustments.all().order_by('-adjustment_date')
    
    context = {
        'loan': loan,
        'risk_assessment': risk_assessment,
        'climate_adjustments': climate_adjustments
    }
    return render(request, 'climate/loan_risk.html', context)

@login_required
def fetch_latest_ndvi(request, farm_id):
    """
    API endpoint to fetch latest NDVI data for a farm
    """
    farm = get_object_or_404(Farm, id=farm_id, farmer=request.user.farmer)
    
    try:
        # Instantiate the NDVI service
        ndvi_service = NDVIService()
        
        # Fetch latest NDVI data
        result = ndvi_service.fetch_and_store_ndvi_data(farm)
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': 'NDVI data updated successfully',
                'data': {
                    'date': result['date'].strftime('%Y-%m-%d'),
                    'ndvi_average': float(result['ndvi_average']),
                    'ndvi_min': float(result['ndvi_min']),
                    'ndvi_max': float(result['ndvi_max'])
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'message': result['message']
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })

@login_required
def weather_forecast_api(request, days=7):
    """
    API endpoint to get weather forecast for the farmer's region
    """
    region = request.user.farmer.region
    
    try:
        # Instantiate the weather service
        weather_service = WeatherService()
        
        # Fetch weather forecast
        forecast_data = weather_service.get_weather_forecast(region, days)
        
        return JsonResponse({
            'success': True,
            'forecast': forecast_data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        })
