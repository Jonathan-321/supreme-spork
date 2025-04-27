from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.credit_dashboard, name='credit_dashboard'),
    path('generate/', views.generate_credit_score, name='generate_credit_score'),
    path('history/', views.credit_history, name='credit_history'),
    path('score/<int:score_id>/', views.score_details, name='score_details'),
    path('scores/', views.score_history, name='score_history'),
    path('api/score/', views.api_get_credit_score, name='api_get_credit_score'),
]
