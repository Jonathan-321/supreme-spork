from django.contrib import admin
from .models import CreditScore, CreditScoreComponent, CreditScoreConfiguration, CreditHistory

@admin.register(CreditScore)
class CreditScoreAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'score', 'generation_date', 'valid_until', 'algorithm_version')
    list_filter = ('algorithm_version', 'generation_date')
    search_fields = ('farmer__farmer_id', 'farmer__user__first_name', 'farmer__user__last_name')
    date_hierarchy = 'generation_date'

@admin.register(CreditScoreComponent)
class CreditScoreComponentAdmin(admin.ModelAdmin):
    list_display = ('credit_score', 'component_name', 'component_value', 'weight')
    list_filter = ('component_name',)
    search_fields = ('credit_score__farmer__farmer_id', 'component_name')

@admin.register(CreditScoreConfiguration)
class CreditScoreConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'is_active', 'date_created')
    list_filter = ('is_active',)
    search_fields = ('name', 'version', 'description')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'version', 'is_active', 'description')
        }),
        ('Component Weights', {
            'fields': (
                'repayment_history_weight',
                'farm_productivity_weight',
                'market_conditions_weight',
                'relationship_length_weight',
                'climate_risk_weight'
            )
        }),
        ('Other Parameters', {
            'fields': (
                'min_months_for_full_relationship_score',
                'productivity_baseline_factor',
                'climate_risk_penalty_factor'
            )
        }),
    )

@admin.register(CreditHistory)
class CreditHistoryAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'event_type', 'event_date', 'loan', 'amount', 'days_late')
    list_filter = ('event_type', 'event_date')
    search_fields = ('farmer__farmer_id', 'farmer__user__first_name', 'farmer__user__last_name', 'loan__loan_id')
    date_hierarchy = 'event_date'
