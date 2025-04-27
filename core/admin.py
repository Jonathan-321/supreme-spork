from django.contrib import admin
from .models import Region, Farmer, Farm, Crop, Harvest, LoanProduct, Loan, Payment

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    search_fields = ('name', 'country')

@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ('farmer_id', 'user', 'type', 'region', 'registration_date', 'is_active')
    list_filter = ('type', 'region', 'is_active')
    search_fields = ('farmer_id', 'user__username', 'user__first_name', 'user__last_name')
    date_hierarchy = 'registration_date'

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ('name', 'farmer', 'area', 'main_crop', 'irrigation', 'date_added')
    list_filter = ('irrigation', 'main_crop')
    search_fields = ('name', 'farmer__farmer_id', 'farmer__user__first_name', 'farmer__user__last_name')
    date_hierarchy = 'date_added'

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ('name', 'scientific_name', 'growing_season_start', 'growing_season_end', 'water_requirement')
    search_fields = ('name', 'scientific_name')

@admin.register(Harvest)
class HarvestAdmin(admin.ModelAdmin):
    list_display = ('farm', 'crop', 'harvest_date', 'yield_amount', 'yield_unit', 'quality_rating')
    list_filter = ('quality_rating', 'crop')
    search_fields = ('farm__name', 'crop__name')
    date_hierarchy = 'harvest_date'

@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_amount', 'max_amount', 'interest_rate', 'term_months', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    filter_horizontal = ('allowed_crops',)

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'farmer', 'product', 'amount', 'status', 'application_date', 'approval_date')
    list_filter = ('status', 'product')
    search_fields = ('loan_id', 'farmer__farmer_id', 'farmer__user__first_name', 'farmer__user__last_name')
    date_hierarchy = 'application_date'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('loan', 'amount', 'payment_date', 'payment_type', 'reference_number')
    list_filter = ('payment_type',)
    search_fields = ('loan__loan_id', 'reference_number')
    date_hierarchy = 'payment_date'
