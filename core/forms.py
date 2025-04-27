from django import forms
from .models import Farmer, Farm, Loan

class FarmerProfileForm(forms.ModelForm):
    """
    Form for updating farmer profile information
    """
    class Meta:
        model = Farmer
        fields = ['phone_number', 'type']
        
    def __init__(self, *args, **kwargs):
        super(FarmerProfileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class FarmForm(forms.ModelForm):
    """
    Form for adding/editing farm details
    """
    class Meta:
        model = Farm
        fields = ['name', 'area', 'main_crop', 'secondary_crops', 
                  'soil_type', 'irrigation']
        
    def __init__(self, *args, **kwargs):
        super(FarmForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

class LoanApplicationForm(forms.ModelForm):
    """
    Form for loan application
    """
    class Meta:
        model = Loan
        fields = ['product', 'amount', 'term_months', 'purpose', 'farm', 'crop']
        
    def __init__(self, *args, **kwargs):
        farmer = kwargs.pop('farmer', None)
        super(LoanApplicationForm, self).__init__(*args, **kwargs)
        
        # Limit farms to those owned by the farmer
        if farmer:
            self.fields['farm'].queryset = Farm.objects.filter(farmer=farmer)
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
