from django.db import models
from django.contrib.gis.db import models as gis_models
from core.models import Region, Farm

class WeatherStation(models.Model):
    """
    Represents a weather station that provides meteorological data
    """
    name = models.CharField(max_length=100)
    station_id = models.CharField(max_length=50, unique=True)
    location = gis_models.PointField()
    elevation = models.DecimalField(max_digits=8, decimal_places=2, help_text="Elevation in meters")
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.station_id})"

class WeatherData(models.Model):
    """
    Stores historical weather data from stations or API sources
    """
    station = models.ForeignKey(WeatherStation, on_delete=models.CASCADE, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    date = models.DateField()
    temperature_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature_min = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature_avg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    precipitation = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Precipitation in mm")
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Relative humidity in %")
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Wind speed in m/s")
    source = models.CharField(max_length=50, help_text="Data source (e.g., 'OpenWeatherMap', 'Station')")
    
    class Meta:
        unique_together = [['station', 'region', 'date', 'source']]
    
    def __str__(self):
        return f"{self.region.name} - {self.date} ({self.source})"

class WeatherForecast(models.Model):
    """
    Stores weather forecast data
    """
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    forecast_date = models.DateField(help_text="Date of the forecast")
    prediction_date = models.DateField(help_text="Date for which the forecast is made")
    temperature_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature_min = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    precipitation_probability = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    precipitation_amount = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Expected precipitation in mm")
    source = models.CharField(max_length=50, help_text="Forecast source (e.g., 'OpenWeatherMap')")
    
    class Meta:
        unique_together = [['region', 'forecast_date', 'prediction_date', 'source']]
    
    def __str__(self):
        return f"{self.region.name} - Forecast on {self.forecast_date} for {self.prediction_date}"

class SatelliteImagery(models.Model):
    """
    Stores metadata for satellite imagery
    """
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    date = models.DateField()
    satellite = models.CharField(max_length=50, help_text="Satellite name (e.g., 'MODIS', 'Sentinel-2')")
    imagery_type = models.CharField(max_length=50, help_text="Type of imagery (e.g., 'NDVI', 'True Color')")
    resolution = models.IntegerField(help_text="Resolution in meters")
    cloud_cover_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    url = models.URLField(max_length=500, help_text="URL to the imagery or API endpoint")
    
    class Meta:
        unique_together = [['region', 'date', 'satellite', 'imagery_type']]
        verbose_name_plural = "Satellite Imagery"
    
    def __str__(self):
        return f"{self.region.name} - {self.date} - {self.imagery_type} ({self.satellite})"

class NDVIData(models.Model):
    """
    Stores NDVI (Normalized Difference Vegetation Index) data for farms
    """
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='ndvi_data')
    date = models.DateField()
    ndvi_average = models.DecimalField(max_digits=5, decimal_places=3, help_text="Average NDVI value (between -1 and 1)")
    ndvi_min = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    ndvi_max = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    source = models.CharField(max_length=50, help_text="Source of NDVI data (e.g., 'NASA MODIS')")
    imagery = models.ForeignKey(SatelliteImagery, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = [['farm', 'date', 'source']]
        verbose_name_plural = "NDVI Data"
    
    def __str__(self):
        return f"{self.farm.name} - {self.date} - NDVI: {self.ndvi_average}"

class ClimateRisk(models.Model):
    """
    Stores climate risk assessments for regions
    """
    RISK_LEVEL_CHOICES = [
        ('LOW', 'Low Risk'),
        ('MEDIUM', 'Medium Risk'),
        ('HIGH', 'High Risk'),
        ('EXTREME', 'Extreme Risk'),
    ]
    
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='climate_risks')
    risk_type = models.CharField(max_length=100, help_text="Type of climate risk (e.g., 'Drought', 'Flood', 'Frost')")
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES)
    assessment_date = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    probability = models.DecimalField(max_digits=5, decimal_places=2, help_text="Probability of occurrence (0-100%)")
    potential_impact = models.TextField()
    mitigation_measures = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = [['region', 'risk_type', 'assessment_date']]
    
    def __str__(self):
        return f"{self.region.name} - {self.risk_type} - {self.risk_level}"

class LoanClimateAdjustment(models.Model):
    """
    Tracks adjustments made to loans based on climate risk factors
    """
    ADJUSTMENT_TYPE_CHOICES = [
        ('TERM_EXTENSION', 'Term Extension'),
        ('PAYMENT_REDUCTION', 'Payment Reduction'),
        ('INTEREST_REDUCTION', 'Interest Rate Reduction'),
        ('PAYMENT_DEFERRAL', 'Payment Deferral'),
        ('SPECIAL_CONDITION', 'Special Condition'),
    ]
    
    loan = models.ForeignKey('core.Loan', on_delete=models.CASCADE, related_name='climate_adjustments')
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPE_CHOICES)
    adjustment_date = models.DateField()
    climate_event = models.CharField(max_length=100, help_text="Description of the climate event triggering adjustment")
    original_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Original value before adjustment")
    adjusted_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Value after adjustment")
    justification = models.TextField()
    approved_by = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.loan.loan_id} - {self.adjustment_type} on {self.adjustment_date}"
