from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.climate_dashboard, name='climate_dashboard'),
    path('farm/<int:farm_id>/', views.farm_climate_data, name='farm_climate_data'),
    path('loan/<str:loan_id>/risk/', views.loan_climate_risk, name='loan_climate_risk'),
    path('api/farm/<int:farm_id>/ndvi/', views.fetch_latest_ndvi, name='fetch_latest_ndvi'),
    path('api/weather/forecast/', views.weather_forecast_api, name='weather_forecast_api'),
    path('api/weather/forecast/<int:days>/', views.weather_forecast_api, name='weather_forecast_api_days'),
]
