from django.db import models
from core.models import Farmer, Loan

class CreditScore(models.Model):
    """
    Stores credit scores generated for farmers
    """
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='credit_scores')
    score = models.IntegerField(help_text="Credit score (0-100)")
    generation_date = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateField(null=True, blank=True)
    algorithm_version = models.CharField(max_length=20, help_text="Version of the scoring algorithm used")
    
    def __str__(self):
        return f"{self.farmer.farmer_id} - {self.score} - {self.generation_date.date()}"

class CreditScoreComponent(models.Model):
    """
    Stores individual components that make up a credit score
    """
    credit_score = models.ForeignKey(CreditScore, on_delete=models.CASCADE, related_name='components')
    component_name = models.CharField(max_length=100, help_text="Name of the score component")
    component_value = models.DecimalField(max_digits=5, decimal_places=2, help_text="Value for this component")
    weight = models.DecimalField(max_digits=5, decimal_places=2, help_text="Weight of this component in the overall score")
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.credit_score.farmer.farmer_id} - {self.component_name}"

class CreditScoreConfiguration(models.Model):
    """
    Configures weights and parameters for the credit scoring algorithm
    """
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)
    
    # Weights for different factors
    repayment_history_weight = models.DecimalField(max_digits=5, decimal_places=2, default=30.0)
    farm_productivity_weight = models.DecimalField(max_digits=5, decimal_places=2, default=20.0)
    market_conditions_weight = models.DecimalField(max_digits=5, decimal_places=2, default=15.0)
    relationship_length_weight = models.DecimalField(max_digits=5, decimal_places=2, default=15.0)
    climate_risk_weight = models.DecimalField(max_digits=5, decimal_places=2, default=20.0)
    
    # Other configuration parameters
    min_months_for_full_relationship_score = models.IntegerField(default=24)
    productivity_baseline_factor = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    climate_risk_penalty_factor = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)
    
    def __str__(self):
        return f"{self.name} v{self.version} ({'Active' if self.is_active else 'Inactive'})"

class CreditHistory(models.Model):
    """
    Stores credit history events for farmers
    """
    EVENT_TYPE_CHOICES = [
        ('LOAN_APPLICATION', 'Loan Application'),
        ('LOAN_APPROVAL', 'Loan Approval'),
        ('LOAN_REJECTION', 'Loan Rejection'),
        ('PAYMENT_ON_TIME', 'Payment On Time'),
        ('PAYMENT_LATE', 'Payment Late'),
        ('PAYMENT_MISSED', 'Payment Missed'),
        ('LOAN_COMPLETED', 'Loan Completed'),
        ('LOAN_DEFAULTED', 'Loan Defaulted'),
        ('LOAN_RESTRUCTURED', 'Loan Restructured'),
    ]
    
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='credit_history')
    loan = models.ForeignKey(Loan, on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    event_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    days_late = models.IntegerField(null=True, blank=True, help_text="Number of days late (for late payments)")
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.farmer.farmer_id} - {self.event_type} - {self.event_date}"
