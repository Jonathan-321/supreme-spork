"""
Credit scoring API routes for the AgriFinance mobile app.
Provides AI-driven credit scoring and loan recommendations for farmers.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import random
import logging
import json

from api.models import Farmer, Farm, Loan, LoanStatus, Payment
from api.models import ClimateRiskAssessment
from api import db

# Configure logging
logger = logging.getLogger('agrifinance_api.credit')

# Create blueprint
credit_api = Blueprint('credit_api', __name__)

@credit_api.route('/score/<int:farmer_id>')
def get_credit_score(farmer_id):
    """
    Get AI-driven credit score for a farmer.
    Uses farm data, loan history, and climate risk to generate a personalized score.
    """
    try:
        farmer = db.session.get(Farmer, farmer_id)
        if not farmer:
            return jsonify({"error": "Farmer not found"}), 404
            
        # In a real app, this would use a trained ML model
        # For demo purposes, we'll generate a realistic score based on available data
        
        # Get farmer's loans
        loans = db.session.query(Loan).filter(Loan.farmer_id == farmer_id).all()
        
        # Get farmer's farms
        farms = db.session.query(Farm).filter(Farm.farmer_id == farmer_id).all()
        
        # Calculate score components
        
        # 1. Repayment history (30%)
        repayment_score = calculate_repayment_score(loans)
        
        # 2. Farm productivity (20%)
        productivity_score = calculate_productivity_score(farms)
        
        # 3. Market conditions (10%)
        # This would use real market data in a production app
        market_score = random.uniform(0.5, 0.8)
        
        # 4. Relationship length (10%)
        # Based on how long the farmer has been registered
        days_registered = (datetime.utcnow() - farmer.registration_date).days if farmer.registration_date else 0
        relationship_score = min(1.0, days_registered / 365)  # Max score after 1 year
        
        # 5. Climate risk (30%)
        climate_score = calculate_climate_score(farms)
        
        # Calculate weighted score (0-100)
        weighted_score = (
            repayment_score * 0.3 +
            productivity_score * 0.2 +
            market_score * 0.1 +
            relationship_score * 0.1 +
            climate_score * 0.3
        ) * 100
        
        # Round to nearest integer
        final_score = round(weighted_score)
        
        # Determine credit rating
        rating = "Poor"
        if final_score >= 80:
            rating = "Excellent"
        elif final_score >= 70:
            rating = "Good"
        elif final_score >= 60:
            rating = "Fair"
        elif final_score >= 50:
            rating = "Marginal"
            
        # Generate loan eligibility based on score
        eligible_loans = generate_eligible_loans(final_score, farms)
        
        # Generate improvement recommendations
        recommendations = generate_recommendations(
            repayment_score,
            productivity_score,
            market_score,
            relationship_score,
            climate_score
        )
        
        return jsonify({
            "farmer_id": farmer_id,
            "score": final_score,
            "rating": rating,
            "components": [
                {"name": "Repayment History", "value": round(repayment_score, 2), "weight": 0.3},
                {"name": "Farm Productivity", "value": round(productivity_score, 2), "weight": 0.2},
                {"name": "Market Conditions", "value": round(market_score, 2), "weight": 0.1},
                {"name": "Relationship Length", "value": round(relationship_score, 2), "weight": 0.1},
                {"name": "Climate Risk", "value": round(climate_score, 2), "weight": 0.3}
            ],
            "eligible_loans": eligible_loans,
            "recommendations": recommendations,
            "last_updated": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error calculating credit score: {str(e)}")
        return jsonify({"error": str(e)}), 500

def calculate_repayment_score(loans):
    """Calculate repayment history score based on loan payment history"""
    if not loans:
        return 0.5  # Neutral score for no history
        
    completed_loans = [loan for loan in loans if loan.status == LoanStatus.COMPLETED]
    active_loans = [loan for loan in loans if loan.is_active()]
    defaulted_loans = [loan for loan in loans if loan.status == LoanStatus.DEFAULTED]
    
    # Perfect score for completed loans with no defaults
    if completed_loans and not defaulted_loans:
        return 0.9
        
    # Penalize for defaults
    if defaulted_loans:
        default_penalty = len(defaulted_loans) / max(1, len(loans))
        return max(0.1, 0.7 - (default_penalty * 0.5))
        
    # For active loans, check payment history
    if active_loans:
        on_time_payments = 0
        total_payments = 0
        
        for loan in active_loans:
            if loan.payments:
                total_payments += len(loan.payments)
                # In a real app, we'd check if payments were on time
                # For demo, assume 80% of payments were on time
                on_time_payments += int(len(loan.payments) * 0.8)
        
        if total_payments > 0:
            return 0.5 + (on_time_payments / total_payments * 0.4)
    
    return 0.5  # Default score

def calculate_productivity_score(farms):
    """Calculate farm productivity score based on NDVI and farm data"""
    if not farms:
        return 0.5  # Neutral score for no farms
        
    # In a real app, this would use actual NDVI data and yield history
    # For demo purposes, use the NDVI values if available
    
    total_score = 0
    scored_farms = 0
    
    for farm in farms:
        if farm.last_ndvi_value is not None:
            # NDVI values typically range from -1 to 1, with healthy vegetation > 0.6
            # Convert to 0-1 scale for our scoring
            farm_score = (farm.last_ndvi_value + 1) / 2
            
            # Weight larger farms more heavily
            weight = min(1.0, farm.size_hectares / 10)  # Cap at 10 hectares
            total_score += farm_score * weight
            scored_farms += weight
    
    if scored_farms > 0:
        return total_score / scored_farms
    
    # If no NDVI data, give a default score based on farm count and size
    if len(farms) >= 3:
        return 0.7  # Multiple farms suggests successful farmer
    elif len(farms) > 0:
        total_size = sum(farm.size_hectares for farm in farms)
        return min(0.8, 0.5 + (total_size / 20))  # Bonus for larger farms
    
    return 0.5  # Default score

def calculate_climate_score(farms):
    """Calculate climate risk score based on risk assessments"""
    if not farms:
        return 0.5  # Neutral score for no farms
        
    # Get the most recent climate risk assessment for each farm
    risk_scores = []
    
    for farm in farms:
        assessment = db.session.query(ClimateRiskAssessment).filter(
            ClimateRiskAssessment.farm_id == farm.id
        ).order_by(ClimateRiskAssessment.assessment_date.desc()).first()
        
        if assessment:
            # Convert risk score (0-100) to 0-1 scale and invert (higher is better)
            risk_scores.append(1 - (assessment.risk_score / 100))
    
    if risk_scores:
        return sum(risk_scores) / len(risk_scores)
    
    # If no risk assessments, give a default score
    return 0.5

def generate_eligible_loans(credit_score, farms):
    """Generate loan products the farmer is eligible for based on credit score"""
    eligible_loans = []
    
    # Calculate total farm area
    total_area = sum(farm.size_hectares for farm in farms) if farms else 0
    
    # Seasonal loan - available to most farmers
    if credit_score >= 50:
        max_amount = min(5000, total_area * 500)
        interest_rate = 12 - (credit_score - 50) / 10  # 12% base, decreasing with score
        
        eligible_loans.append({
            "type": "Seasonal",
            "max_amount": max_amount,
            "interest_rate": round(interest_rate, 1),
            "term_months": 6,
            "description": "Short-term financing for seeds, fertilizer, and labor",
            "requirements": ["At least one registered farm", "Credit score 50+"]
        })
    
    # Equipment loan - medium credit requirement
    if credit_score >= 65:
        max_amount = min(10000, total_area * 1000)
        interest_rate = 15 - (credit_score - 65) / 8  # 15% base, decreasing with score
        
        eligible_loans.append({
            "type": "Equipment",
            "max_amount": max_amount,
            "interest_rate": round(interest_rate, 1),
            "term_months": 24,
            "description": "Medium-term financing for farm equipment and tools",
            "requirements": ["Credit score 65+", "At least 6 months of history"]
        })
    
    # Infrastructure loan - higher credit requirement
    if credit_score >= 75:
        max_amount = min(25000, total_area * 2000)
        interest_rate = 14 - (credit_score - 75) / 10  # 14% base, decreasing with score
        
        eligible_loans.append({
            "type": "Infrastructure",
            "max_amount": max_amount,
            "interest_rate": round(interest_rate, 1),
            "term_months": 36,
            "description": "Long-term financing for irrigation systems, storage facilities, or land improvements",
            "requirements": ["Credit score 75+", "At least 1 year of history", "Completed previous loans"]
        })
    
    # Emergency loan - available to established farmers
    if credit_score >= 60:
        max_amount = min(3000, total_area * 300)
        interest_rate = 18 - (credit_score - 60) / 5  # 18% base, decreasing with score
        
        eligible_loans.append({
            "type": "Emergency",
            "max_amount": max_amount,
            "interest_rate": round(interest_rate, 1),
            "term_months": 12,
            "description": "Quick financing for unexpected challenges like equipment failure or pest outbreaks",
            "requirements": ["Credit score 60+", "At least one active or completed loan"]
        })
    
    # Expansion loan - highest credit requirement
    if credit_score >= 80:
        max_amount = min(50000, total_area * 5000)
        interest_rate = 13 - (credit_score - 80) / 10  # 13% base, decreasing with score
        
        eligible_loans.append({
            "type": "Expansion",
            "max_amount": max_amount,
            "interest_rate": round(interest_rate, 1),
            "term_months": 60,
            "description": "Long-term financing for expanding farm operations, purchasing land, or major investments",
            "requirements": ["Credit score 80+", "Excellent repayment history", "At least 2 years of history"]
        })
    
    return eligible_loans

def generate_recommendations(repayment_score, productivity_score, market_score, relationship_score, climate_score):
    """Generate personalized recommendations to improve credit score"""
    recommendations = []
    
    # Repayment history recommendations
    if repayment_score < 0.7:
        recommendations.append({
            "component": "Repayment History",
            "actions": [
                "Make all loan payments on time",
                "Consider setting up automatic payments",
                "If struggling with payments, contact us before missing a payment"
            ]
        })
    
    # Farm productivity recommendations
    if productivity_score < 0.7:
        recommendations.append({
            "component": "Farm Productivity",
            "actions": [
                "Consider crop diversification to reduce risk",
                "Implement recommended farming practices for your crops",
                "Register all your farms to provide a complete picture of productivity"
            ]
        })
    
    # Market conditions recommendations
    if market_score < 0.7:
        recommendations.append({
            "component": "Market Conditions",
            "actions": [
                "Consider crops with stable market demand",
                "Explore direct-to-consumer selling options",
                "Join a cooperative to access better markets"
            ]
        })
    
    # Relationship length recommendations
    if relationship_score < 0.7:
        recommendations.append({
            "component": "Relationship Length",
            "actions": [
                "Maintain your account activity",
                "Update your farm information regularly",
                "Consider starting with a small loan to build history"
            ]
        })
    
    # Climate risk recommendations
    if climate_score < 0.7:
        recommendations.append({
            "component": "Climate Risk",
            "actions": [
                "Implement recommended climate mitigation strategies",
                "Consider drought-resistant crop varieties",
                "Invest in irrigation or water management systems"
            ]
        })
    
    return recommendations
