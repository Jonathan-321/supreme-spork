from django.contrib import admin
from .models import (
    WeatherStation, WeatherData, WeatherForecast, SatelliteImagery,
    NDVIData, ClimateRisk, LoanClimateAdjustment
)

@admin.register(WeatherStation)
class WeatherStationAdmin(admin.ModelAdmin):
    list_display = ('name', 'station_id', 'region', 'elevation', 'active')
    list_filter = ('active', 'region')
    search_fields = ('name', 'station_id')

@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ('region', 'date', 'temperature_avg', 'precipitation', 'source')
    list_filter = ('source', 'region')
    date_hierarchy = 'date'
    search_fields = ('region__name', 'source')

@admin.register(WeatherForecast)
class WeatherForecastAdmin(admin.ModelAdmin):
    list_display = ('region', 'forecast_date', 'prediction_date', 'temperature_max', 'precipitation_probability', 'source')
    list_filter = ('source', 'region')
    date_hierarchy = 'prediction_date'
    search_fields = ('region__name', 'source')

@admin.register(SatelliteImagery)
class SatelliteImageryAdmin(admin.ModelAdmin):
    list_display = ('region', 'date', 'satellite', 'imagery_type', 'resolution', 'cloud_cover_percentage')
    list_filter = ('satellite', 'imagery_type', 'region')
    date_hierarchy = 'date'
    search_fields = ('region__name', 'satellite', 'imagery_type')

@admin.register(NDVIData)
class NDVIDataAdmin(admin.ModelAdmin):
    list_display = ('farm', 'date', 'ndvi_average', 'ndvi_min', 'ndvi_max', 'source')
    list_filter = ('source',)
    date_hierarchy = 'date'
    search_fields = ('farm__name', 'farm__farmer__farmer_id', 'source')

@admin.register(ClimateRisk)
class ClimateRiskAdmin(admin.ModelAdmin):
    list_display = ('region', 'risk_type', 'risk_level', 'assessment_date', 'valid_until', 'probability')
    list_filter = ('risk_level', 'risk_type', 'region')
    date_hierarchy = 'assessment_date'
    search_fields = ('region__name', 'risk_type')

@admin.register(LoanClimateAdjustment)
class LoanClimateAdjustmentAdmin(admin.ModelAdmin):
    list_display = ('loan', 'adjustment_type', 'adjustment_date', 'climate_event', 'original_value', 'adjusted_value')
    list_filter = ('adjustment_type',)
    date_hierarchy = 'adjustment_date'
    search_fields = ('loan__loan_id', 'climate_event', 'approved_by')
