from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.farmer_detail, name='farmer_detail'),
    path('loans/', views.loan_list, name='loan_list'),
    path('loans/<str:loan_id>/', views.loan_detail, name='loan_detail'),
]
