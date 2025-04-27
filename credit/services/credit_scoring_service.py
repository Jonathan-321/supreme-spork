import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from django.db.models import Avg, Count, Sum, F, Q
from django.utils import timezone
from ..models import CreditScore, CreditScoreComponent, CreditScoreConfiguration, CreditHistory
from core.models import Farmer, Loan, Farm, Harvest, Payment
from climate.models import ClimateRisk, NDVIData
from climate.services.climate_risk_service import ClimateRiskService

class DynamicCreditScoringService:
    """
    Service for generating dynamic credit scores for farmers based on multiple factors.
    
    This service considers:
    - Loan repayment history
    - Farm productivity
    - Market conditions
    - Relationship length with platform
    - Climate risk factors
    """
    
    def __init__(self, config=None):
        """
        Initialize the credit scoring service
        
        Args:
            config (CreditScoreConfiguration, optional): Configuration to use for scoring.
                If None, the latest active configuration will be used.
        """
        # Get active configuration
        if config is None:
            try:
                self.config = CreditScoreConfiguration.objects.filter(is_active=True).latest('date_created')
            except CreditScoreConfiguration.DoesNotExist:
                # Create a default configuration if none exists
                self.config = CreditScoreConfiguration.objects.create(
                    name="Default Configuration",
                    version="1.0.0",
                    is_active=True,
                    description="Default credit scoring configuration"
                )
        else:
            self.config = config
        
        # Initialize climate risk service
        self.climate_risk_service = ClimateRiskService()
        
        # Set the algorithm version
        self.algorithm_version = self.config.version
    
    def generate_credit_score(self, farmer):
        """
        Generate a credit score for a farmer
        
        Args:
            farmer (Farmer): The farmer to score
            
        Returns:
            dict: Result containing credit score and component details
        """
        try:
            # Calculate individual score components
            repayment_history = self._calculate_repayment_history_score(farmer)
            farm_productivity = self._calculate_farm_productivity_score(farmer)
            market_conditions = self._calculate_market_conditions_score(farmer)
            relationship_length = self._calculate_relationship_length_score(farmer)
            climate_risk = self._calculate_climate_risk_score(farmer)
            
            # Apply configured weights
            weighted_scores = {
                'Repayment History': repayment_history * float(self.config.repayment_history_weight),
                'Farm Productivity': farm_productivity * float(self.config.farm_productivity_weight),
                'Market Conditions': market_conditions * float(self.config.market_conditions_weight),
                'Relationship Length': relationship_length * float(self.config.relationship_length_weight),
                'Climate Risk': climate_risk * float(self.config.climate_risk_weight)
            }
            
            # Calculate total score from weighted components
            total_weight = float(self.config.repayment_history_weight) + \
                           float(self.config.farm_productivity_weight) + \
                           float(self.config.market_conditions_weight) + \
                           float(self.config.relationship_length_weight) + \
                           float(self.config.climate_risk_weight)
            
            # Normalize to 0-100 scale
            total_score = sum(weighted_scores.values()) / total_weight * 100
            total_score = min(100, max(0, round(total_score)))
            
            # Create a new credit score record
            credit_score = CreditScore.objects.create(
                farmer=farmer,
                score=total_score,
                algorithm_version=self.algorithm_version,
                valid_until=datetime.now().date() + timedelta(days=30)  # Valid for 30 days
            )
            
            # Create component records
            components = []
            for name, weighted_value in weighted_scores.items():
                raw_value = weighted_value / float(getattr(self.config, f"{name.lower().replace(' ', '_')}_weight"))
                weight = float(getattr(self.config, f"{name.lower().replace(' ', '_')}_weight"))
                
                component = CreditScoreComponent.objects.create(
                    credit_score=credit_score,
                    component_name=name,
                    component_value=raw_value,
                    weight=weight,
                    description=self._get_component_description(name, raw_value)
                )
                components.append(component)
            
            return {
                'success': True,
                'credit_score': credit_score,
                'components': components,
                'raw_scores': {
                    'repayment_history': repayment_history,
                    'farm_productivity': farm_productivity,
                    'market_conditions': market_conditions,
                    'relationship_length': relationship_length,
                    'climate_risk': climate_risk
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'message': f"Error generating credit score: {str(e)}"
            }
    
    def _calculate_repayment_history_score(self, farmer):
        """
        Calculate repayment history score component
        
        Args:
            farmer (Farmer): The farmer to evaluate
            
        Returns:
            float: Score from 0 to 1
        """
        # Get loan and payment history
        loans = Loan.objects.filter(farmer=farmer)
        
        if not loans.exists():
            # No loan history available
            return 0.5  # Neutral score for no history
        
        # Get credit history events
        credit_events = CreditHistory.objects.filter(farmer=farmer).order_by('event_date')
        
        # If no credit events recorded, analyze loan data
        if not credit_events.exists():
            # This is a fallback if the credit history hasn't been properly recorded
            self._generate_credit_history_from_loans(farmer)
            credit_events = CreditHistory.objects.filter(farmer=farmer).order_by('event_date')
            
            # If still no events, return neutral score
            if not credit_events.exists():
                return 0.5
        
        # Calculate scores for different event types
        
        # Count negative events
        negative_events = credit_events.filter(
            event_type__in=['PAYMENT_LATE', 'PAYMENT_MISSED', 'LOAN_DEFAULTED']
        ).count()
        
        # Count positive events
        positive_events = credit_events.filter(
            event_type__in=['PAYMENT_ON_TIME', 'LOAN_COMPLETED']
        ).count()
        
        # Calculate total repayment events
        total_repayment_events = credit_events.filter(
            event_type__in=['PAYMENT_ON_TIME', 'PAYMENT_LATE', 'PAYMENT_MISSED']
        ).count()
        
        if total_repayment_events == 0:
            # No repayment history yet
            return 0.5
        
        # Calculate on-time payment ratio
        on_time_ratio = positive_events / total_repayment_events if total_repayment_events > 0 else 0
        
        # Calculate recency weighted score
        # Recent events have more impact
        recent_score = self._calculate_recent_repayment_score(credit_events)
        
        # Completed loans bonus
        completed_loans = loans.filter(status='COMPLETED').count()
        completed_bonus = min(0.1, 0.02 * completed_loans)  # Up to 10% bonus for 5+ completed loans
        
        # Defaults penalty
        defaults = loans.filter(status='DEFAULTED').count()
        default_penalty = min(0.5, 0.1 * defaults)  # Up to 50% penalty for 5+ defaults
        
        # Combine factors
        base_score = on_time_ratio * 0.6 + recent_score * 0.4
        final_score = base_score + completed_bonus - default_penalty
        
        # Normalize to 0-1
        return min(1.0, max(0.0, final_score))
    
    def _calculate_recent_repayment_score(self, credit_events):
        """
        Calculate a score based on recent repayment behavior
        
        Args:
            credit_events (QuerySet): Credit history events
            
        Returns:
            float: Score from 0 to 1
        """
        # Get repayment events from the last 12 months
        one_year_ago = datetime.now().date() - timedelta(days=365)
        recent_events = credit_events.filter(
            event_date__gte=one_year_ago,
            event_type__in=['PAYMENT_ON_TIME', 'PAYMENT_LATE', 'PAYMENT_MISSED']
        )
        
        if not recent_events.exists():
            return 0.5  # Neutral score if no recent history
        
        # Count different event types
        on_time = recent_events.filter(event_type='PAYMENT_ON_TIME').count()
        late = recent_events.filter(event_type='PAYMENT_LATE').count()
        missed = recent_events.filter(event_type='PAYMENT_MISSED').count()
        
        # Calculate weighted score
        total = on_time + late + missed
        score = (on_time + 0.5 * late) / total if total > 0 else 0.5
        
        return score
    
    def _generate_credit_history_from_loans(self, farmer):
        """
        Generate credit history events from loan and payment data
        
        Args:
            farmer (Farmer): The farmer to generate history for
        """
        # Get all loans for the farmer
        loans = Loan.objects.filter(farmer=farmer)
        
        # Process each loan
        for loan in loans:
            # Record loan application
            CreditHistory.objects.get_or_create(
                farmer=farmer,
                loan=loan,
                event_type='LOAN_APPLICATION',
                event_date=loan.application_date,
                amount=loan.amount,
                defaults={
                    'notes': f"Applied for {loan.product.name} loan"
                }
            )
            
            # Record loan approval/rejection
            if loan.status in ['APPROVED', 'DISBURSED', 'REPAYING', 'COMPLETED']:
                if loan.approval_date:
                    CreditHistory.objects.get_or_create(
                        farmer=farmer,
                        loan=loan,
                        event_type='LOAN_APPROVAL',
                        event_date=loan.approval_date,
                        amount=loan.amount,
                        defaults={
                            'notes': f"Loan {loan.loan_id} approved"
                        }
                    )
            elif loan.status == 'REJECTED':
                CreditHistory.objects.get_or_create(
                    farmer=farmer,
                    loan=loan,
                    event_type='LOAN_REJECTION',
                    event_date=loan.application_date + timedelta(days=7),  # Assuming week-long process
                    amount=loan.amount,
                    defaults={
                        'notes': f"Loan {loan.loan_id} rejected"
                    }
                )
            
            # Record loan completion/default
            if loan.status == 'COMPLETED' and loan.actual_completion_date:
                CreditHistory.objects.get_or_create(
                    farmer=farmer,
                    loan=loan,
                    event_type='LOAN_COMPLETED',
                    event_date=loan.actual_completion_date,
                    amount=loan.amount,
                    defaults={
                        'notes': f"Loan {loan.loan_id} completed successfully"
                    }
                )
            elif loan.status == 'DEFAULTED':
                CreditHistory.objects.get_or_create(
                    farmer=farmer,
                    loan=loan,
                    event_type='LOAN_DEFAULTED',
                    event_date=loan.expected_completion_date or (loan.disbursement_date + timedelta(days=30*loan.term_months)),
                    amount=loan.amount,
                    defaults={
                        'notes': f"Loan {loan.loan_id} defaulted"
                    }
                )
            
            # Record payments
            payments = Payment.objects.filter(loan=loan)
            for payment in payments:
                # Determine if payment was on time or late
                # For simplicity, assuming payments are expected monthly
                if loan.disbursement_date:
                    # Calculate expected payment date
                    # This is simplified and would need to be improved in a real system
                    month_number = (payment.payment_date.year - loan.disbursement_date.year) * 12 + payment.payment_date.month - loan.disbursement_date.month
                    expected_date = datetime(
                        loan.disbursement_date.year + ((loan.disbursement_date.month + month_number - 1) // 12),
                        ((loan.disbursement_date.month + month_number - 1) % 12) + 1,
                        min(loan.disbursement_date.day, 28)
                    ).date()
                    
                    days_late = (payment.payment_date - expected_date).days if payment.payment_date > expected_date else 0
                    
                    if days_late > 30:
                        event_type = 'PAYMENT_MISSED'  # Considered missed if more than 30 days late
                    elif days_late > 0:
                        event_type = 'PAYMENT_LATE'
                    else:
                        event_type = 'PAYMENT_ON_TIME'
                    
                    CreditHistory.objects.get_or_create(
                        farmer=farmer,
                        loan=loan,
                        event_type=event_type,
                        event_date=payment.payment_date,
                        amount=payment.amount,
                        days_late=days_late if days_late > 0 else None,
                        defaults={
                            'notes': f"Payment {payment.reference_number or ''} for loan {loan.loan_id}"
                        }
                    )
    
    def _calculate_farm_productivity_score(self, farmer):
        """
        Calculate farm productivity score component based on farm performance,
        harvest data, and NDVI satellite data
        
        Args:
            farmer (Farmer): The farmer to evaluate
            
        Returns:
            float: Score from 0 to 1
        """
        # Get all farms for the farmer
        farms = Farm.objects.filter(farmer=farmer)
        
        if not farms.exists():
            return 0.5  # Neutral score if no farms
        
        # Calculate productivity score for each farm
        farm_scores = []
        
        for farm in farms:
            # Get harvests for the farm
            harvests = Harvest.objects.filter(farm=farm).order_by('-harvest_date')
            
            # Get NDVI data for the farm
            ndvi_data = NDVIData.objects.filter(farm=farm).order_by('-date')
            
            farm_score = self._calculate_single_farm_productivity(farm, harvests, ndvi_data)
            farm_scores.append((farm_score, farm.area))  # Score and weight by area
        
        # Calculate weighted average by farm area
        if farm_scores:
            total_area = sum(float(area) for _, area in farm_scores)
            weighted_score = sum(score * float(area) for score, area in farm_scores) / total_area if total_area > 0 else 0.5
        else:
            weighted_score = 0.5
        
        return min(1.0, max(0.0, weighted_score))
    
    def _calculate_single_farm_productivity(self, farm, harvests, ndvi_data):
        """
        Calculate productivity score for a single farm
        
        Args:
            farm (Farm): The farm to evaluate
            harvests (QuerySet): Harvest records for the farm
            ndvi_data (QuerySet): NDVI data records for the farm
            
        Returns:
            float: Score from 0 to 1
        """
        # Initialize component scores
        harvest_score = 0.5
        ndvi_score = 0.5
        
        # Calculate harvest score if available
        if harvests.exists():
            # Consider yield and quality
            avg_quality = harvests.aggregate(Avg('quality_rating'))['quality_rating__avg'] or 3  # Default to average
            
            # Normalize quality to 0-1 scale (1-5 scale in the model)
            quality_score = (avg_quality - 1) / 4  # Scale from 1-5 to 0-1
            
            # Compare recent harvests to historical ones if enough data
            if harvests.count() > 2:
                # Get most recent harvest
                recent_harvest = harvests.first()
                
                # Get previous harvests of the same crop
                previous_harvests = harvests.filter(crop=recent_harvest.crop).exclude(id=recent_harvest.id)
                
                if previous_harvests.exists():
                    avg_previous_yield = previous_harvests.aggregate(Avg('yield_amount'))['yield_amount__avg'] or 0
                    
                    # Calculate yield improvement ratio
                    if avg_previous_yield > 0:
                        current_yield = float(recent_harvest.yield_amount)
                        yield_ratio = current_yield / avg_previous_yield
                        
                        # Cap improvement at 200% (2.0)
                        yield_score = min(1.0, yield_ratio / 2)
                    else:
                        yield_score = 0.5
                else:
                    yield_score = 0.5
            else:
                yield_score = 0.5
            
            # Combine quality and yield scores
            harvest_score = quality_score * 0.4 + yield_score * 0.6
        
        # Calculate NDVI score if available
        if ndvi_data.exists():
            # Get most recent NDVI
            recent_ndvi = ndvi_data.first()
            
            # NDVI values range from -1 to 1, with higher values indicating healthier vegetation
            # Typical healthy vegetation has NDVI > 0.6
            ndvi_value = float(recent_ndvi.ndvi_average)
            
            # Convert NDVI to a 0-1 score
            # Scale from -0.2 to 0.8 to cover most agricultural values
            ndvi_score = min(1.0, max(0.0, (ndvi_value + 0.2) / 1.0))
            
            # Check NDVI trend if enough data
            if ndvi_data.count() > 3:
                older_ndvi = ndvi_data[3:min(6, ndvi_data.count())].aggregate(Avg('ndvi_average'))['ndvi_average__avg'] or 0
                
                # Calculate trend factor
                if older_ndvi > 0:
                    trend_factor = (ndvi_value / older_ndvi) - 0.5  # -0.5 to normalize
                    
                    # Adjust NDVI score by trend
                    ndvi_score = min(1.0, max(0.0, ndvi_score + trend_factor * 0.2))
        
        # Combine harvest and NDVI scores
        # Weight harvest data higher if more harvests are available
        if harvests.count() > 2:
            combined_score = harvest_score * 0.7 + ndvi_score * 0.3
        else:
            combined_score = harvest_score * 0.4 + ndvi_score * 0.6
        
        # Apply irrigation bonus (if the farm has irrigation, it's less risky)
        if farm.irrigation:
            combined_score = min(1.0, combined_score * 1.1)  # 10% bonus for irrigation
        
        return combined_score
    
    def _calculate_market_conditions_score(self, farmer):
        """
        Calculate market conditions score component
        
        Args:
            farmer (Farmer): The farmer to evaluate
            
        Returns:
            float: Score from 0 to 1
        """
        # In a real system, this would incorporate market data for the farmer's crops
        # For this implementation, we'll use a simplified approach
        
        # Get the farmer's main crops
        farms = Farm.objects.filter(farmer=farmer)
        
        if not farms.exists():
            return 0.5  # Neutral score
        
        # Get all main crops
        main_crops = [farm.main_crop for farm in farms]
        
        # In a real system, we would fetch current market prices and trends for these crops
        # For this implementation, we'll use a simulated market score based on the region
        
        # Get farmer's region
        region = farmer.region
        
        if not region:
            return 0.5  # Neutral score if no region
        
        # Simulate market conditions based on region and current month
        # In a real system, this would be based on actual market data
        current_month = datetime.now().month
        
        # Simplified seasonal market factor
        # Assumes better market conditions during harvest seasons (varies by hemisphere)
        if region.country.lower() in ['south africa', 'kenya', 'nigeria', 'ghana', 'ethiopia']:
            # Simplified seasons for major African agricultural countries
            if current_month in [3, 4, 5]:  # Spring/harvest season in some regions
                season_factor = 0.7
            elif current_month in [9, 10, 11]:  # Another harvest season
                season_factor = 0.8
            else:
                season_factor = 0.5
        else:
            # Default seasonal pattern
            if current_month in [3, 4, 5, 9, 10, 11]:
                season_factor = 0.6
            else:
                season_factor = 0.5
        
        # In a real implementation, we would incorporate:
        # - Current market prices compared to historical averages
        # - Price volatility
        # - Export opportunities
        # - Market demand forecasts
        
        # For now, return a simplified market conditions score
        market_score = season_factor
        
        return market_score
    
    def _calculate_relationship_length_score(self, farmer):
        """
        Calculate relationship length score component
        
        Args:
            farmer (Farmer): The farmer to evaluate
            
        Returns:
            float: Score from 0 to 1
        """
        # Calculate the duration of the relationship in months
        registration_date = farmer.registration_date
        months_active = ((datetime.now().date() - registration_date).days) / 30
        
        # Determine score based on relationship length
        min_months_for_full_score = self.config.min_months_for_full_relationship_score
        
        if months_active >= min_months_for_full_score:
            # Full score for long-term farmers
            relationship_score = 1.0
        else:
            # Proportional score for newer farmers
            relationship_score = months_active / min_months_for_full_score
        
        # Adjust based on activity level
        loans_count = Loan.objects.filter(farmer=farmer).count()
        
        # Activity bonus for farmers with multiple loans
        if loans_count > 1:
            activity_bonus = min(0.2, 0.05 * loans_count)  # Up to 20% bonus
            relationship_score = min(1.0, relationship_score + activity_bonus)
        
        return relationship_score
    
    def _calculate_climate_risk_score(self, farmer):
        """
        Calculate climate risk score component
        
        Args:
            farmer (Farmer): The farmer to evaluate
            
        Returns:
            float: Score from 0 to 1
        """
        # Get region
        region = farmer.region
        
        if not region:
            return 0.5  # Neutral score if no region
        
        # Get climate risk assessment
        climate_risk = self.climate_risk_service.assess_climate_risk_for_region(region)
        
        # Map risk levels to scores
        risk_level_scores = {
            'EXTREME': 0.1,
            'HIGH': 0.3,
            'MEDIUM': 0.5,
            'LOW': 0.7,
            'MINIMAL': 0.9,
            'UNKNOWN': 0.5,  # Neutral score for unknown risk
            'ERROR': 0.5
        }
        
        overall_risk_level = climate_risk['overall_risk']['risk_level']
        base_score = risk_level_scores.get(overall_risk_level, 0.5)
        
        # Get farms for additional assessment
        farms = Farm.objects.filter(farmer=farmer)
        
        if farms.exists():
            # Calculate farm vulnerability scores
            farm_vulnerability_scores = []
            
            for farm in farms:
                vulnerability = self.climate_risk_service.assess_farm_vulnerability(farm)
                
                vulnerability_scores = {
                    'LOW': 0.8,
                    'MEDIUM': 0.5,
                    'HIGH': 0.2,
                    'UNKNOWN': 0.5,
                    'ERROR': 0.5
                }
                
                vuln_score = vulnerability_scores.get(vulnerability['vulnerability_level'], 0.5)
                farm_vulnerability_scores.append((vuln_score, farm.area))  # Score and weight
            
            # Calculate weighted average vulnerability by farm area
            if farm_vulnerability_scores:
                total_area = sum(float(area) for _, area in farm_vulnerability_scores)
                avg_vulnerability = sum(score * float(area) for score, area in farm_vulnerability_scores) / total_area if total_area > 0 else 0.5
            else:
                avg_vulnerability = 0.5
            
            # Combine regional risk and farm vulnerability
            climate_score = base_score * 0.6 + avg_vulnerability * 0.4
        else:
            climate_score = base_score
        
        # Apply climate risk penalty factor
        penalty_factor = float(self.config.climate_risk_penalty_factor)
        if penalty_factor != 1.0:
            # Adjust only negative scores if penalty factor > 1
            if climate_score < 0.5 and penalty_factor > 1:
                climate_score = 0.5 - ((0.5 - climate_score) * penalty_factor)
            # Adjust all scores if penalty factor < 1
            elif penalty_factor < 1:
                climate_score = 0.5 + ((climate_score - 0.5) / penalty_factor)
        
        return min(1.0, max(0.0, climate_score))
    
    def _get_component_description(self, component_name, score_value):
        """
        Generate a description for a score component
        
        Args:
            component_name (str): Name of the component
            score_value (float): Raw score value (0-1)
            
        Returns:
            str: Description of the score component
        """
        # Map score ranges to descriptive text
        score_descriptors = {
            (0.0, 0.2): "Very Poor",
            (0.2, 0.4): "Poor",
            (0.4, 0.6): "Average",
            (0.6, 0.8): "Good",
            (0.8, 1.01): "Excellent"  # 1.01 to include exactly 1.0
        }
        
        # Find the appropriate descriptor
        descriptor = "Unknown"
        for score_range, desc in score_descriptors.items():
            if score_range[0] <= score_value < score_range[1]:
                descriptor = desc
                break
        
        # Component-specific descriptions
        descriptions = {
            'Repayment History': {
                "Very Poor": "Significant issues with loan repayments or defaults.",
                "Poor": "Multiple late payments or missed payments.",
                "Average": "Some late payments but generally meets obligations.",
                "Good": "Consistent on-time payments with rare exceptions.",
                "Excellent": "Perfect or near-perfect repayment history."
            },
            'Farm Productivity': {
                "Very Poor": "Substantially below-average farm productivity.",
                "Poor": "Below-average productivity compared to similar farms.",
                "Average": "Average productivity for the region and crop types.",
                "Good": "Above-average productivity and crop yields.",
                "Excellent": "Exceptional farm productivity and crop health."
            },
            'Market Conditions': {
                "Very Poor": "Extremely unfavorable market for farmer's crops.",
                "Poor": "Below-average market conditions affecting profitability.",
                "Average": "Stable market conditions with normal price fluctuations.",
                "Good": "Favorable market conditions for farmer's main crops.",
                "Excellent": "Highly favorable market with strong demand and prices."
            },
            'Relationship Length': {
                "Very Poor": "New customer with very limited platform history.",
                "Poor": "Short relationship history with the platform.",
                "Average": "Moderate length relationship with the platform.",
                "Good": "Established relationship with good activity level.",
                "Excellent": "Long-term, active customer of the platform."
            },
            'Climate Risk': {
                "Very Poor": "Extreme climate risk factors affecting farm operations.",
                "Poor": "High climate risk with significant potential impact.",
                "Average": "Moderate climate risk typical for the region.",
                "Good": "Low climate risk with minimal potential impact.",
                "Excellent": "Minimal climate risk or excellent mitigation measures."
            }
        }
        
        return descriptions.get(component_name, {}).get(descriptor, f"{descriptor} {component_name} score.")
