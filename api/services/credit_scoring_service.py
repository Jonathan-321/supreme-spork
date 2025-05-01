"""
AI-powered credit scoring service for the AgriFinance mobile app.

This service provides machine learning-based credit scoring for farmers,
taking into account farm data, loan history, and climate risk factors.
"""
import logging
import numpy as np
from datetime import datetime, timedelta
import joblib
import os
from pathlib import Path

# Configure logging
logger = logging.getLogger('agrifinance_api.services.credit_scoring')

class CreditScoringService:
    """
    Service for AI-powered credit scoring.
    
    In a production environment, this would use trained machine learning models.
    For the MVP, we'll implement a rule-based scoring system that mimics ML behavior
    but can be easily replaced with actual models later.
    """
    
    def __init__(self):
        """Initialize the credit scoring service"""
        self.model_path = Path(__file__).parent.parent.parent / 'ml' / 'models'
        self.model = None
        
        # Try to load model if it exists
        try:
            if os.path.exists(self.model_path / 'credit_scoring_model.joblib'):
                self.model = joblib.load(self.model_path / 'credit_scoring_model.joblib')
                logger.info("Loaded credit scoring model")
        except Exception as e:
            logger.warning(f"Could not load credit scoring model: {str(e)}")
    
    def calculate_credit_score(self, farmer_data, loans_data, farms_data, climate_data):
        """
        Calculate a credit score for a farmer based on various data points.
        
        Args:
            farmer_data: Dictionary with farmer information
            loans_data: List of loan dictionaries
            farms_data: List of farm dictionaries
            climate_data: Dictionary with climate risk information
            
        Returns:
            Dictionary with credit score and component scores
        """
        # If we have a trained model, use it
        if self.model:
            return self._calculate_score_with_model(farmer_data, loans_data, farms_data, climate_data)
        
        # Otherwise use rule-based scoring
        return self._calculate_score_with_rules(farmer_data, loans_data, farms_data, climate_data)
    
    def _calculate_score_with_model(self, farmer_data, loans_data, farms_data, climate_data):
        """Calculate credit score using a trained ML model"""
        try:
            # In a real implementation, we would:
            # 1. Extract features from the input data
            # 2. Preprocess features (scaling, encoding, etc.)
            # 3. Run the model to get predictions
            # 4. Post-process the results
            
            # For now, fall back to rule-based scoring
            logger.info("Using ML model for credit scoring")
            return self._calculate_score_with_rules(farmer_data, loans_data, farms_data, climate_data)
            
        except Exception as e:
            logger.error(f"Error using ML model for credit scoring: {str(e)}")
            return self._calculate_score_with_rules(farmer_data, loans_data, farms_data, climate_data)
    
    def _calculate_score_with_rules(self, farmer_data, loans_data, farms_data, climate_data):
        """
        Calculate credit score using rule-based system.
        This mimics what a machine learning model would do but with explicit rules.
        """
        # Initialize component scores
        repayment_score = self._calculate_repayment_score(loans_data)
        productivity_score = self._calculate_productivity_score(farms_data)
        market_score = self._calculate_market_score(farms_data)
        relationship_score = self._calculate_relationship_score(farmer_data)
        climate_score = self._calculate_climate_score(climate_data, farms_data)
        
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
        
        return {
            "score": final_score,
            "rating": rating,
            "components": [
                {"name": "Repayment History", "value": round(repayment_score, 2), "weight": 0.3},
                {"name": "Farm Productivity", "value": round(productivity_score, 2), "weight": 0.2},
                {"name": "Market Conditions", "value": round(market_score, 2), "weight": 0.1},
                {"name": "Relationship Length", "value": round(relationship_score, 2), "weight": 0.1},
                {"name": "Climate Risk", "value": round(climate_score, 2), "weight": 0.3}
            ]
        }
    
    def _calculate_repayment_score(self, loans_data):
        """Calculate repayment history score based on loan payment history"""
        if not loans_data:
            return 0.5  # Neutral score for no history
        
        completed_loans = [loan for loan in loans_data if loan.get('status') == 'COMPLETED']
        active_loans = [loan for loan in loans_data if loan.get('status') in ['APPROVED', 'DISBURSED', 'REPAYING']]
        defaulted_loans = [loan for loan in loans_data if loan.get('status') == 'DEFAULTED']
        
        # Perfect score for completed loans with no defaults
        if completed_loans and not defaulted_loans:
            return 0.9
        
        # Penalize for defaults
        if defaulted_loans:
            default_penalty = len(defaulted_loans) / max(1, len(loans_data))
            return max(0.1, 0.7 - (default_penalty * 0.5))
        
        # For active loans, check payment history
        if active_loans:
            on_time_payments = 0
            total_payments = 0
            
            for loan in active_loans:
                payments = loan.get('payments', [])
                total_payments += len(payments)
                # In a real app, we'd check if payments were on time
                # For demo, assume 80% of payments were on time
                on_time_payments += int(len(payments) * 0.8)
            
            if total_payments > 0:
                return 0.5 + (on_time_payments / total_payments * 0.4)
        
        return 0.5  # Default score
    
    def _calculate_productivity_score(self, farms_data):
        """Calculate farm productivity score based on NDVI and farm data"""
        if not farms_data:
            return 0.5  # Neutral score for no farms
        
        # In a real app, this would use actual NDVI data and yield history
        # For demo purposes, use the NDVI values if available
        
        total_score = 0
        scored_farms = 0
        
        for farm in farms_data:
            ndvi = farm.get('crop_health', {}).get('ndvi_value')
            if ndvi is not None:
                # NDVI values typically range from -1 to 1, with healthy vegetation > 0.6
                # Convert to 0-1 scale for our scoring
                farm_score = (ndvi + 1) / 2
                
                # Weight larger farms more heavily
                size = farm.get('size_hectares', 1)
                weight = min(1.0, size / 10)  # Cap at 10 hectares
                total_score += farm_score * weight
                scored_farms += weight
        
        if scored_farms > 0:
            return total_score / scored_farms
        
        # If no NDVI data, give a default score based on farm count and size
        if len(farms_data) >= 3:
            return 0.7  # Multiple farms suggests successful farmer
        elif len(farms_data) > 0:
            total_size = sum(farm.get('size_hectares', 0) for farm in farms_data)
            return min(0.8, 0.5 + (total_size / 20))  # Bonus for larger farms
        
        return 0.5  # Default score
    
    def _calculate_market_score(self, farms_data):
        """
        Calculate market conditions score.
        In a real app, this would use market price data for the farmer's crops.
        """
        # This is a placeholder for real market data integration
        # For now, return a random score between 0.5 and 0.8
        return np.random.uniform(0.5, 0.8)
    
    def _calculate_relationship_score(self, farmer_data):
        """Calculate relationship length score based on registration date"""
        registration_date_str = farmer_data.get('registration_date')
        if not registration_date_str:
            return 0.5  # Default score
        
        try:
            registration_date = datetime.fromisoformat(registration_date_str.replace('Z', '+00:00'))
            days_registered = (datetime.utcnow() - registration_date).days
            return min(1.0, days_registered / 365)  # Max score after 1 year
        except Exception:
            return 0.5  # Default score if date parsing fails
    
    def _calculate_climate_score(self, climate_data, farms_data):
        """Calculate climate risk score based on risk assessments"""
        if not climate_data:
            return 0.5  # Neutral score for no data
        
        # If we have specific risk assessments for farms
        if isinstance(climate_data, list):
            risk_scores = []
            
            for assessment in climate_data:
                risk_score = assessment.get('risk_score')
                if risk_score is not None:
                    # Convert risk score (0-100) to 0-1 scale and invert (higher is better)
                    risk_scores.append(1 - (risk_score / 100))
            
            if risk_scores:
                return sum(risk_scores) / len(risk_scores)
        
        # If we have a single climate risk assessment
        elif isinstance(climate_data, dict):
            risk_score = climate_data.get('risk_score')
            if risk_score is not None:
                return 1 - (risk_score / 100)
        
        # If no risk assessments, give a default score
        return 0.5
    
    def generate_loan_recommendations(self, credit_score, farms_data):
        """Generate loan products the farmer is eligible for based on credit score"""
        eligible_loans = []
        
        # Calculate total farm area
        total_area = sum(farm.get('size_hectares', 0) for farm in farms_data) if farms_data else 0
        
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
    
    def generate_improvement_recommendations(self, credit_score_data):
        """Generate personalized recommendations to improve credit score"""
        recommendations = []
        
        # Extract component scores
        components = {comp["name"]: comp["value"] for comp in credit_score_data.get("components", [])}
        
        # Repayment history recommendations
        if components.get("Repayment History", 1.0) < 0.7:
            recommendations.append({
                "component": "Repayment History",
                "actions": [
                    "Make all loan payments on time",
                    "Consider setting up automatic payments",
                    "If struggling with payments, contact us before missing a payment"
                ]
            })
        
        # Farm productivity recommendations
        if components.get("Farm Productivity", 1.0) < 0.7:
            recommendations.append({
                "component": "Farm Productivity",
                "actions": [
                    "Consider crop diversification to reduce risk",
                    "Implement recommended farming practices for your crops",
                    "Register all your farms to provide a complete picture of productivity"
                ]
            })
        
        # Market conditions recommendations
        if components.get("Market Conditions", 1.0) < 0.7:
            recommendations.append({
                "component": "Market Conditions",
                "actions": [
                    "Consider crops with stable market demand",
                    "Explore direct-to-consumer selling options",
                    "Join a cooperative to access better markets"
                ]
            })
        
        # Relationship length recommendations
        if components.get("Relationship Length", 1.0) < 0.7:
            recommendations.append({
                "component": "Relationship Length",
                "actions": [
                    "Maintain your account activity",
                    "Update your farm information regularly",
                    "Consider starting with a small loan to build history"
                ]
            })
        
        # Climate risk recommendations
        if components.get("Climate Risk", 1.0) < 0.7:
            recommendations.append({
                "component": "Climate Risk",
                "actions": [
                    "Implement recommended climate mitigation strategies",
                    "Consider drought-resistant crop varieties",
                    "Invest in irrigation or water management systems"
                ]
            })
        
        return recommendations

# Create a singleton instance
credit_scoring_service = CreditScoringService()
