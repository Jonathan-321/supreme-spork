from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import CreditScore, CreditScoreComponent, CreditHistory
from .services.credit_scoring_service import DynamicCreditScoringService
from core.models import Farmer, Loan

@login_required
def credit_dashboard(request):
    """
    Dashboard view showing credit information for a farmer
    """
    try:
        farmer = request.user.farmer
        
        # Get the latest credit score
        latest_score = CreditScore.objects.filter(farmer=farmer).order_by('-generation_date').first()
        
        # If no score exists or score is older than 30 days, generate a new one
        if not latest_score or (latest_score.valid_until and latest_score.valid_until < datetime.now().date()):
            credit_service = DynamicCreditScoringService()
            score_result = credit_service.generate_credit_score(farmer)
            latest_score = score_result['credit_score']
        
        # Get score components
        if latest_score:
            components = CreditScoreComponent.objects.filter(credit_score=latest_score)
        else:
            components = []
        
        # Get credit history
        credit_history = CreditHistory.objects.filter(farmer=farmer).order_by('-event_date')[:20]
        
        # Prepare component data for chart
        component_labels = [c.component_name for c in components]
        component_values = [float(c.component_value) for c in components]
        component_weights = [float(c.weight) for c in components]
        
        context = {
            'farmer': farmer,
            'credit_score': latest_score,
            'components': components,
            'credit_history': credit_history,
            'component_labels': component_labels,
            'component_values': component_values,
            'component_weights': component_weights
        }
        return render(request, 'credit/dashboard.html', context)
    except Farmer.DoesNotExist:
        return redirect('home')

@login_required
def generate_credit_score(request):
    """
    Generate a new credit score for the farmer
    """
    if request.method == 'POST':
        try:
            farmer = request.user.farmer
            
            # Generate a new score
            credit_service = DynamicCreditScoringService()
            result = credit_service.generate_credit_score(farmer)
            
            if result['success']:
                return redirect('credit_dashboard')
            else:
                return render(request, 'credit/error.html', {'message': result['message']})
        except Farmer.DoesNotExist:
            return redirect('home')
    else:
        return redirect('credit_dashboard')

@login_required
def credit_history(request):
    """
    View showing detailed credit history for a farmer
    """
    try:
        farmer = request.user.farmer
        
        # Get complete credit history
        history = CreditHistory.objects.filter(farmer=farmer).order_by('-event_date')
        
        # Group events by loan
        loans = Loan.objects.filter(farmer=farmer)
        loan_history = {}
        
        for loan in loans:
            loan_events = CreditHistory.objects.filter(loan=loan).order_by('-event_date')
            loan_history[loan.loan_id] = {
                'loan': loan,
                'events': loan_events
            }
        
        context = {
            'farmer': farmer,
            'credit_history': history,
            'loan_history': loan_history
        }
        return render(request, 'credit/history.html', context)
    except Farmer.DoesNotExist:
        return redirect('home')

@login_required
def score_details(request, score_id):
    """
    View showing detailed information about a specific credit score
    """
    try:
        farmer = request.user.farmer
        score = get_object_or_404(CreditScore, id=score_id, farmer=farmer)
        
        # Get score components
        components = CreditScoreComponent.objects.filter(credit_score=score)
        
        context = {
            'farmer': farmer,
            'score': score,
            'components': components
        }
        return render(request, 'credit/score_details.html', context)
    except Farmer.DoesNotExist:
        return redirect('home')

@login_required
def score_history(request):
    """
    View showing the history of credit scores for a farmer
    """
    try:
        farmer = request.user.farmer
        
        # Get all scores
        scores = CreditScore.objects.filter(farmer=farmer).order_by('-generation_date')
        
        # Prepare data for chart
        dates = [score.generation_date.strftime('%Y-%m-%d') for score in scores]
        values = [score.score for score in scores]
        
        context = {
            'farmer': farmer,
            'scores': scores,
            'score_dates': dates,
            'score_values': values
        }
        return render(request, 'credit/score_history.html', context)
    except Farmer.DoesNotExist:
        return redirect('home')

@login_required
def api_get_credit_score(request):
    """
    API endpoint to get the latest credit score for a farmer
    """
    try:
        farmer = request.user.farmer
        
        # Get the latest credit score
        latest_score = CreditScore.objects.filter(farmer=farmer).order_by('-generation_date').first()
        
        if latest_score:
            return JsonResponse({
                'success': True,
                'score': latest_score.score,
                'generation_date': latest_score.generation_date.strftime('%Y-%m-%d'),
                'valid_until': latest_score.valid_until.strftime('%Y-%m-%d') if latest_score.valid_until else None,
                'algorithm_version': latest_score.algorithm_version
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'No credit score available. Please generate a new score.'
            })
    except Farmer.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Farmer profile not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
