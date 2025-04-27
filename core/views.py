from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Farmer, Farm, Loan, Payment, LoanProduct
from credit.services.credit_scoring_service import DynamicCreditScoringService

@login_required
def home(request):
    """
    Home page view
    """
    # Check if user has a farmer profile
    try:
        farmer = request.user.farmer
        farms = Farm.objects.filter(farmer=farmer)
        loans = Loan.objects.filter(farmer=farmer)
        
        context = {
            'farmer': farmer,
            'farms_count': farms.count(),
            'active_loans_count': loans.filter(status__in=['APPROVED', 'DISBURSED', 'REPAYING']).count(),
            'total_loans_count': loans.count()
        }
        return render(request, 'home.html', context)
    except Farmer.DoesNotExist:
        messages.warning(request, "You don't have a farmer profile. Please contact an administrator.")
        return render(request, 'home.html')

@login_required
def dashboard(request):
    """
    Dashboard view with overview of farmer's loans and farms
    """
    try:
        farmer = request.user.farmer
        farms = Farm.objects.filter(farmer=farmer)
        active_loans = Loan.objects.filter(
            farmer=farmer, 
            status__in=['APPROVED', 'DISBURSED', 'REPAYING']
        )
        
        # Get credit score for the farmer
        credit_service = DynamicCreditScoringService()
        credit_score = credit_service.generate_credit_score(farmer)
        
        eligible_products = LoanProduct.objects.filter(
            is_active=True,
            min_credit_score__lte=credit_score
        )
        
        context = {
            'farmer': farmer,
            'farms': farms,
            'active_loans': active_loans,
            'credit_score': credit_score,
            'eligible_products': eligible_products
        }
        return render(request, 'dashboard.html', context)
    except Farmer.DoesNotExist:
        messages.warning(request, "You don't have a farmer profile. Please contact an administrator.")
        return redirect('home')

@login_required
def farmer_detail(request):
    """
    Farmer profile detail view
    """
    try:
        farmer = request.user.farmer
        farms = Farm.objects.filter(farmer=farmer)
        
        context = {
            'farmer': farmer,
            'farms': farms,
        }
        return render(request, 'farmers/detail.html', context)
    except Farmer.DoesNotExist:
        messages.warning(request, "You don't have a farmer profile. Please contact an administrator.")
        return redirect('home')

@login_required
def loan_list(request):
    """
    View to list all loans for a farmer
    """
    try:
        farmer = request.user.farmer
        loans = Loan.objects.filter(farmer=farmer).order_by('-application_date')
        
        context = {
            'loans': loans
        }
        return render(request, 'loans/list.html', context)
    except Farmer.DoesNotExist:
        messages.warning(request, "You don't have a farmer profile. Please contact an administrator.")
        return redirect('home')

@login_required
def loan_detail(request, loan_id):
    """
    View to show details of a specific loan
    """
    try:
        farmer = request.user.farmer
        loan = get_object_or_404(Loan, loan_id=loan_id, farmer=farmer)
        payments = Payment.objects.filter(loan=loan).order_by('-payment_date')
        
        # Calculate remaining balance
        total_paid = sum(payment.amount for payment in payments)
        remaining_balance = loan.amount - total_paid
        
        context = {
            'loan': loan,
            'payments': payments,
            'total_paid': total_paid,
            'remaining_balance': remaining_balance
        }
        return render(request, 'loans/detail.html', context)
    except Farmer.DoesNotExist:
        messages.warning(request, "You don't have a farmer profile. Please contact an administrator.")
        return redirect('home')
