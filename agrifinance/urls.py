"""
URL configuration for agrifinance project.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='home')),
    path('core/', include('core.urls')),
    path('climate/', include('climate.urls')),
    path('credit/', include('credit.urls')),
]
