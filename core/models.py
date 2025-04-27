from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models

class Region(models.Model):
    """
    Represents a geographical region where farmers operate
    """
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    area = gis_models.PolygonField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name}, {self.country}"

class Farmer(models.Model):
    """
    Represents a farmer who can apply for loans
    """
    USER_TYPE_CHOICES = [
        ('INDIVIDUAL', 'Individual Farmer'),
        ('COOPERATIVE', 'Farming Cooperative'),
        ('AGRIBUSINESS', 'Agribusiness'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    farmer_id = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='INDIVIDUAL')
    phone_number = models.CharField(max_length=20)
    national_id = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)
    location = gis_models.PointField(null=True, blank=True)
    registration_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.farmer_id})"

class Farm(models.Model):
    """
    Represents a farm owned by a farmer
    """
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='farms')
    name = models.CharField(max_length=100)
    area = models.DecimalField(max_digits=10, decimal_places=2, help_text="Area in hectares")
    location = gis_models.PolygonField()
    main_crop = models.CharField(max_length=100)
    secondary_crops = models.CharField(max_length=200, blank=True, null=True)
    soil_type = models.CharField(max_length=100, blank=True, null=True)
    irrigation = models.BooleanField(default=False)
    date_added = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.farmer.farmer_id})"

class Crop(models.Model):
    """
    Represents a crop type with its characteristics
    """
    name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=100, blank=True, null=True)
    growing_season_start = models.IntegerField(help_text="Month number (1-12)")
    growing_season_end = models.IntegerField(help_text="Month number (1-12)")
    water_requirement = models.IntegerField(help_text="Water requirement in mm")
    optimal_temperature_min = models.DecimalField(max_digits=5, decimal_places=2)
    optimal_temperature_max = models.DecimalField(max_digits=5, decimal_places=2)
    
    def __str__(self):
        return self.name

class Harvest(models.Model):
    """
    Represents a harvest record for a farm
    """
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='harvests')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    harvest_date = models.DateField()
    yield_amount = models.DecimalField(max_digits=10, decimal_places=2)
    yield_unit = models.CharField(max_length=20, default="kg")
    quality_rating = models.IntegerField(choices=[(1, 'Poor'), (2, 'Below Average'), 
                                                 (3, 'Average'), (4, 'Good'), (5, 'Excellent')])
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.crop.name} - {self.harvest_date} - {self.farm.name}"

class LoanProduct(models.Model):
    """
    Represents a loan product offered by the platform
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    min_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Annual interest rate in percentage")
    term_months = models.IntegerField()
    grace_period_days = models.IntegerField(default=0)
    processing_fee = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    allowed_crops = models.ManyToManyField(Crop, blank=True)
    min_credit_score = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Loan(models.Model):
    """
    Represents a loan issued to a farmer
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('DISBURSED', 'Disbursed'),
        ('REPAYING', 'Repaying'),
        ('COMPLETED', 'Completed'),
        ('DEFAULTED', 'Defaulted'),
        ('RESTRUCTURED', 'Restructured'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    loan_id = models.CharField(max_length=50, unique=True)
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='loans')
    product = models.ForeignKey(LoanProduct, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_months = models.IntegerField()
    purpose = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    application_date = models.DateField(auto_now_add=True)
    approval_date = models.DateField(null=True, blank=True)
    disbursement_date = models.DateField(null=True, blank=True)
    expected_completion_date = models.DateField(null=True, blank=True)
    actual_completion_date = models.DateField(null=True, blank=True)
    farm = models.ForeignKey(Farm, on_delete=models.SET_NULL, null=True, blank=True)
    crop = models.ForeignKey(Crop, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.loan_id} - {self.farmer.user.get_full_name()}"

class Payment(models.Model):
    """
    Represents a payment made towards a loan
    """
    PAYMENT_TYPE_CHOICES = [
        ('SCHEDULED', 'Scheduled Payment'),
        ('EXTRA', 'Extra Payment'),
        ('LATE', 'Late Payment'),
    ]
    
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='SCHEDULED')
    reference_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.loan.loan_id} - {self.payment_date} - {self.amount}"
