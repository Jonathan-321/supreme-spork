import numpy as np
from datetime import datetime, timedelta
from django.db.models import Avg, Max, Min
from ..models import ClimateRisk, WeatherData, NDVIData, LoanClimateAdjustment
from core.models import Loan, Farm, Region, Crop

class ClimateRiskService:
    """
    Service for assessing climate risks for agricultural loans
    """
    
    def __init__(self):
        """
        Initialize the climate risk service
        """
        self.risk_thresholds = {
            'drought': {
                'precipitation_threshold': 15,  # mm/month
                'temperature_threshold': 2.0,  # degree C above average
                'ndvi_threshold': -0.2  # NDVI decrease
            },
            'flood': {
                'precipitation_threshold': 150  # mm/day
            },
            'frost': {
                'temperature_threshold': 0  # degree C
            },
            'heat_wave': {
                'temperature_threshold': 35,  # degree C
                'duration_threshold': 3  # days
            }
        }
    
    def assess_drought_risk(self, region, period_days=90):
        """
        Assess drought risk for a region
        
        Args:
            region (Region): Region to assess
            period_days (int): Analysis period in days
            
        Returns:
            dict: Drought risk assessment
        """
        # Get the analysis period
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=period_days)
        
        try:
            # Get weather data for the period
            weather_data = WeatherData.objects.filter(
                region=region,
                date__gte=start_date,
                date__lte=end_date
            )
            
            if not weather_data:
                return {
                    'risk_type': 'DROUGHT',
                    'risk_level': 'UNKNOWN',
                    'probability': 0,
                    'message': 'Insufficient weather data for analysis'
                }
            
            # Calculate average precipitation for the period
            avg_precipitation = weather_data.aggregate(Avg('precipitation'))['precipitation__avg'] or 0
            
            # Get baseline precipitation (from historical data if available)
            historical_start = end_date - timedelta(days=365*2)  # 2 years of data
            historical_end = end_date - timedelta(days=period_days)  # Exclude current period
            
            historical_data = WeatherData.objects.filter(
                region=region,
                date__gte=historical_start,
                date__lte=historical_end
            )
            
            if historical_data:
                baseline_precipitation = historical_data.aggregate(Avg('precipitation'))['precipitation__avg'] or 0
            else:
                # If no historical data, use a default value
                baseline_precipitation = 50  # Default 50mm/month
            
            # Calculate precipitation anomaly
            precip_anomaly = (avg_precipitation - baseline_precipitation) / baseline_precipitation if baseline_precipitation > 0 else 0
            
            # Determine risk level
            drought_threshold = self.risk_thresholds['drought']['precipitation_threshold']
            
            if avg_precipitation < drought_threshold * 0.5:
                risk_level = 'EXTREME'
                probability = 0.9
            elif avg_precipitation < drought_threshold:
                risk_level = 'HIGH'
                probability = 0.7
            elif precip_anomaly < -0.3:
                risk_level = 'MEDIUM'
                probability = 0.5
            elif precip_anomaly < -0.1:
                risk_level = 'LOW'
                probability = 0.3
            else:
                risk_level = 'MINIMAL'
                probability = 0.1
            
            return {
                'risk_type': 'DROUGHT',
                'risk_level': risk_level,
                'probability': probability,
                'avg_precipitation': avg_precipitation,
                'baseline_precipitation': baseline_precipitation,
                'precip_anomaly': precip_anomaly
            }
            
        except Exception as e:
            return {
                'risk_type': 'DROUGHT',
                'risk_level': 'ERROR',
                'probability': 0,
                'message': f'Error assessing drought risk: {str(e)}'
            }
    
    def assess_flood_risk(self, region, period_days=30):
        """
        Assess flood risk for a region
        
        Args:
            region (Region): Region to assess
            period_days (int): Analysis period in days
            
        Returns:
            dict: Flood risk assessment
        """
        # Get the analysis period
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=period_days)
        
        try:
            # Get weather data for the period
            weather_data = WeatherData.objects.filter(
                region=region,
                date__gte=start_date,
                date__lte=end_date
            )
            
            if not weather_data:
                return {
                    'risk_type': 'FLOOD',
                    'risk_level': 'UNKNOWN',
                    'probability': 0,
                    'message': 'Insufficient weather data for analysis'
                }
            
            # Calculate maximum daily precipitation
            max_precipitation = weather_data.aggregate(Max('precipitation'))['precipitation__max'] or 0
            
            # Calculate average daily precipitation
            avg_precipitation = weather_data.aggregate(Avg('precipitation'))['precipitation__avg'] or 0
            
            # Determine risk level based on maximum daily precipitation
            flood_threshold = self.risk_thresholds['flood']['precipitation_threshold']
            
            if max_precipitation > flood_threshold * 1.5:
                risk_level = 'EXTREME'
                probability = 0.9
            elif max_precipitation > flood_threshold:
                risk_level = 'HIGH'
                probability = 0.7
            elif max_precipitation > flood_threshold * 0.7:
                risk_level = 'MEDIUM'
                probability = 0.5
            elif max_precipitation > flood_threshold * 0.5:
                risk_level = 'LOW'
                probability = 0.3
            else:
                risk_level = 'MINIMAL'
                probability = 0.1
            
            return {
                'risk_type': 'FLOOD',
                'risk_level': risk_level,
                'probability': probability,
                'max_precipitation': max_precipitation,
                'avg_precipitation': avg_precipitation
            }
            
        except Exception as e:
            return {
                'risk_type': 'FLOOD',
                'risk_level': 'ERROR',
                'probability': 0,
                'message': f'Error assessing flood risk: {str(e)}'
            }
    
    def assess_temperature_extremes_risk(self, region, period_days=30):
        """
        Assess temperature extremes (heat waves and frost) risk for a region
        
        Args:
            region (Region): Region to assess
            period_days (int): Analysis period in days
            
        Returns:
            dict: Temperature extremes risk assessment
        """
        # Get the analysis period
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=period_days)
        
        try:
            # Get weather data for the period
            weather_data = WeatherData.objects.filter(
                region=region,
                date__gte=start_date,
                date__lte=end_date
            ).order_by('date')
            
            if not weather_data:
                return {
                    'risk_type': 'TEMPERATURE_EXTREMES',
                    'risk_level': 'UNKNOWN',
                    'probability': 0,
                    'message': 'Insufficient weather data for analysis'
                }
            
            # Extract temperature values
            max_temps = [float(data.temperature_max) for data in weather_data if data.temperature_max is not None]
            min_temps = [float(data.temperature_min) for data in weather_data if data.temperature_min is not None]
            
            if not max_temps or not min_temps:
                return {
                    'risk_type': 'TEMPERATURE_EXTREMES',
                    'risk_level': 'UNKNOWN',
                    'probability': 0,
                    'message': 'Insufficient temperature data for analysis'
                }
            
            # Assess heat wave risk
            heat_threshold = self.risk_thresholds['heat_wave']['temperature_threshold']
            duration_threshold = self.risk_thresholds['heat_wave']['duration_threshold']
            
            # Count consecutive days above threshold
            max_consecutive_hot_days = 0
            current_consecutive = 0
            
            for temp in max_temps:
                if temp >= heat_threshold:
                    current_consecutive += 1
                else:
                    max_consecutive_hot_days = max(max_consecutive_hot_days, current_consecutive)
                    current_consecutive = 0
            
            # Update in case the last streak was the maximum
            max_consecutive_hot_days = max(max_consecutive_hot_days, current_consecutive)
            
            # Assess frost risk
            frost_threshold = self.risk_thresholds['frost']['temperature_threshold']
            frost_days = sum(1 for temp in min_temps if temp <= frost_threshold)
            
            # Determine overall risk level
            if max_consecutive_hot_days >= duration_threshold * 2 or frost_days >= 5:
                risk_level = 'EXTREME'
                probability = 0.9
            elif max_consecutive_hot_days >= duration_threshold or frost_days >= 3:
                risk_level = 'HIGH'
                probability = 0.7
            elif max_consecutive_hot_days >= duration_threshold / 2 or frost_days >= 1:
                risk_level = 'MEDIUM'
                probability = 0.5
            elif max(max_temps) > heat_threshold or min(min_temps) < frost_threshold + 2:
                risk_level = 'LOW'
                probability = 0.3
            else:
                risk_level = 'MINIMAL'
                probability = 0.1
            
            return {
                'risk_type': 'TEMPERATURE_EXTREMES',
                'risk_level': risk_level,
                'probability': probability,
                'max_temperature': max(max_temps),
                'min_temperature': min(min_temps),
                'consecutive_hot_days': max_consecutive_hot_days,
                'frost_days': frost_days
            }
            
        except Exception as e:
            return {
                'risk_type': 'TEMPERATURE_EXTREMES',
                'risk_level': 'ERROR',
                'probability': 0,
                'message': f'Error assessing temperature extremes risk: {str(e)}'
            }
    
    def assess_climate_risk_for_region(self, region):
        """
        Assess overall climate risk for a region
        
        Args:
            region (Region): Region to assess
            
        Returns:
            dict: Overall climate risk assessment
        """
        try:
            # Assess individual risks
            drought_risk = self.assess_drought_risk(region)
            flood_risk = self.assess_flood_risk(region)
            temp_risk = self.assess_temperature_extremes_risk(region)
            
            # Combine risks to determine overall risk
            risks = [drought_risk, flood_risk, temp_risk]
            
            # Map risk levels to numerical values
            risk_values = {
                'EXTREME': 4,
                'HIGH': 3,
                'MEDIUM': 2,
                'LOW': 1,
                'MINIMAL': 0,
                'UNKNOWN': None,
                'ERROR': None
            }
            
            # Calculate overall risk level
            valid_risks = [risk for risk in risks if risk['risk_level'] in risk_values and risk_values[risk['risk_level']] is not None]
            
            if not valid_risks:
                overall_risk_level = 'UNKNOWN'
                overall_probability = 0
            else:
                # Get the highest risk level
                max_risk = max(valid_risks, key=lambda x: risk_values[x['risk_level']])
                overall_risk_level = max_risk['risk_level']
                overall_probability = max_risk['probability']
            
            # Store the risk assessment in the database
            risk_record, created = ClimateRisk.objects.update_or_create(
                region=region,
                risk_type='OVERALL',
                assessment_date=datetime.now().date(),
                defaults={
                    'risk_level': overall_risk_level,
                    'valid_until': datetime.now().date() + timedelta(days=30),  # Valid for 30 days
                    'probability': overall_probability,
                    'potential_impact': 'Multiple climate risks including drought, flood, and temperature extremes',
                    'mitigation_measures': 'Monitor weather forecasts, implement irrigation/drainage, adjust planting schedules'
                }
            )
            
            # Return detailed risk assessment
            return {
                'overall_risk': {
                    'risk_level': overall_risk_level,
                    'probability': overall_probability
                },
                'drought_risk': drought_risk,
                'flood_risk': flood_risk,
                'temperature_risk': temp_risk,
                'risk_record_id': risk_record.id
            }
            
        except Exception as e:
            return {
                'overall_risk': {
                    'risk_level': 'ERROR',
                    'probability': 0,
                    'message': f'Error assessing overall climate risk: {str(e)}'
                }
            }
    
    def assess_farm_vulnerability(self, farm):
        """
        Assess a farm's vulnerability to climate risks
        
        Args:
            farm (Farm): Farm to assess
            
        Returns:
            dict: Farm vulnerability assessment
        """
        try:
            # Get NDVI data for the farm
            ndvi_data = NDVIData.objects.filter(farm=farm).order_by('-date')[:12]  # Last 12 records
            
            if not ndvi_data:
                return {
                    'vulnerability_level': 'UNKNOWN',
                    'message': 'Insufficient NDVI data for assessment'
                }
            
            # Calculate NDVI variability
            ndvi_values = [float(data.ndvi_average) for data in ndvi_data]
            ndvi_variability = np.std(ndvi_values) if len(ndvi_values) > 1 else 0
            
            # Assess vulnerability based on irrigation and NDVI variability
            if farm.irrigation:
                if ndvi_variability < 0.05:
                    vulnerability = 'LOW'
                elif ndvi_variability < 0.1:
                    vulnerability = 'MEDIUM'
                else:
                    vulnerability = 'HIGH'
            else:
                if ndvi_variability < 0.08:
                    vulnerability = 'MEDIUM'
                else:
                    vulnerability = 'HIGH'
            
            return {
                'vulnerability_level': vulnerability,
                'ndvi_variability': ndvi_variability,
                'has_irrigation': farm.irrigation
            }
            
        except Exception as e:
            return {
                'vulnerability_level': 'ERROR',
                'message': f'Error assessing farm vulnerability: {str(e)}'
            }
    
    def calculate_climate_adjusted_loan_terms(self, loan):
        """
        Calculate climate-adjusted loan terms based on risk assessment
        
        Args:
            loan (Loan): Loan to adjust
            
        Returns:
            dict: Adjusted loan terms
        """
        try:
            # Get farm associated with the loan
            farm = loan.farm
            
            if not farm:
                return {
                    'success': False,
                    'message': 'No farm associated with this loan'
                }
            
            # Get region
            region = farm.farmer.region
            
            # Assess climate risk for the region
            climate_risk = self.assess_climate_risk_for_region(region)
            
            # Assess farm vulnerability
            vulnerability = self.assess_farm_vulnerability(farm)
            
            # Get current loan terms
            original_terms = {
                'amount': float(loan.amount),
                'interest_rate': float(loan.interest_rate),
                'term_months': loan.term_months
            }
            
            # Default to original terms
            adjusted_terms = original_terms.copy()
            
            # Apply adjustments based on risk and vulnerability
            overall_risk_level = climate_risk['overall_risk']['risk_level']
            
            if overall_risk_level in ['HIGH', 'EXTREME'] and vulnerability['vulnerability_level'] in ['MEDIUM', 'HIGH']:
                # High risk situation - adjust terms
                
                # Extend loan term
                term_extension = 0
                if overall_risk_level == 'EXTREME':
                    term_extension = 6  # 6 months extension for extreme risk
                elif overall_risk_level == 'HIGH':
                    term_extension = 3  # 3 months extension for high risk
                
                adjusted_terms['term_months'] = original_terms['term_months'] + term_extension
                
                # Adjust interest rate for high vulnerability
                if vulnerability['vulnerability_level'] == 'HIGH':
                    # Reduce interest rate slightly
                    interest_reduction = 0.5  # 0.5 percentage points
                    adjusted_terms['interest_rate'] = max(0, original_terms['interest_rate'] - interest_reduction)
            
            # Calculate adjustment ratios
            adjustments = {
                'term_ratio': adjusted_terms['term_months'] / original_terms['term_months'],
                'interest_ratio': adjusted_terms['interest_rate'] / original_terms['interest_rate'] if original_terms['interest_rate'] > 0 else 1,
                'amount_ratio': adjusted_terms['amount'] / original_terms['amount']
            }
            
            return {
                'success': True,
                'original_terms': original_terms,
                'adjusted_terms': adjusted_terms,
                'adjustments': adjustments,
                'climate_risk': climate_risk['overall_risk'],
                'farm_vulnerability': vulnerability
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error calculating climate-adjusted loan terms: {str(e)}'
            }
    
    def apply_climate_adjustment_to_loan(self, loan, adjustment_type, climate_event, new_value, justification, approved_by):
        """
        Apply and record a climate-based adjustment to a loan
        
        Args:
            loan (Loan): Loan to adjust
            adjustment_type (str): Type of adjustment
            climate_event (str): Description of the climate event
            new_value (float): New value after adjustment
            justification (str): Justification for the adjustment
            approved_by (str): Person who approved the adjustment
            
        Returns:
            tuple: (success, message, adjustment object)
        """
        try:
            # Determine the original value based on adjustment type
            if adjustment_type == 'TERM_EXTENSION':
                original_value = loan.term_months
                # Update loan term
                loan.term_months = int(new_value)
                loan.expected_completion_date = (loan.disbursement_date + timedelta(days=30 * int(new_value))) if loan.disbursement_date else None
                loan.save()
            elif adjustment_type == 'INTEREST_REDUCTION':
                original_value = loan.interest_rate
                # Update interest rate
                loan.interest_rate = new_value
                loan.save()
            elif adjustment_type == 'PAYMENT_REDUCTION':
                # For payment reduction, original value would be calculated from loan terms
                # This is a simplified implementation
                original_value = loan.amount / loan.term_months
            elif adjustment_type == 'PAYMENT_DEFERRAL':
                # For deferral, original value could be the original next payment date
                # Simplified implementation
                original_value = datetime.now().timestamp()
            else:
                original_value = 0
            
            # Create adjustment record
            adjustment = LoanClimateAdjustment.objects.create(
                loan=loan,
                adjustment_type=adjustment_type,
                adjustment_date=datetime.now().date(),
                climate_event=climate_event,
                original_value=original_value,
                adjusted_value=new_value,
                justification=justification,
                approved_by=approved_by
            )
            
            return True, f"Successfully applied {adjustment_type} adjustment to loan {loan.loan_id}", adjustment
            
        except Exception as e:
            return False, f"Error applying climate adjustment: {str(e)}", None
    
    def assess_loan_climate_risk(self, loan):
        """
        Assess climate risk for a specific loan
        
        Args:
            loan (Loan): Loan to assess
            
        Returns:
            dict: Risk assessment for the loan
        """
        try:
            # Get farm and region
            farm = loan.farm
            
            if not farm:
                return {
                    'success': False,
                    'message': 'No farm associated with this loan'
                }
            
            region = farm.farmer.region
            
            # Get crop if available
            crop = loan.crop
            
            # Assess regional climate risk
            climate_risk = self.assess_climate_risk_for_region(region)
            
            # Assess farm vulnerability
            vulnerability = self.assess_farm_vulnerability(farm)
            
            # Calculate crop-specific risk if crop data is available
            crop_risk = None
            if crop:
                # This would use crop data to determine specific vulnerabilities
                # For now, a simplified implementation
                crop_risk = {
                    'crop_name': crop.name,
                    'growing_season': (crop.growing_season_start, crop.growing_season_end),
                    'water_requirement': crop.water_requirement,
                    'optimal_temp_range': (float(crop.optimal_temperature_min), float(crop.optimal_temperature_max))
                }
            
            # Calculate overall loan risk level
            regional_risk_level = climate_risk['overall_risk']['risk_level']
            farm_vulnerability = vulnerability['vulnerability_level']
            
            # Risk matrix: combine regional risk and farm vulnerability
            risk_matrix = {
                'EXTREME': {'HIGH': 'EXTREME', 'MEDIUM': 'HIGH', 'LOW': 'MEDIUM', 'UNKNOWN': 'HIGH'},
                'HIGH': {'HIGH': 'HIGH', 'MEDIUM': 'MEDIUM', 'LOW': 'LOW', 'UNKNOWN': 'MEDIUM'},
                'MEDIUM': {'HIGH': 'MEDIUM', 'MEDIUM': 'MEDIUM', 'LOW': 'LOW', 'UNKNOWN': 'LOW'},
                'LOW': {'HIGH': 'LOW', 'MEDIUM': 'LOW', 'LOW': 'MINIMAL', 'UNKNOWN': 'LOW'},
                'MINIMAL': {'HIGH': 'LOW', 'MEDIUM': 'MINIMAL', 'LOW': 'MINIMAL', 'UNKNOWN': 'MINIMAL'},
                'UNKNOWN': {'HIGH': 'MEDIUM', 'MEDIUM': 'MEDIUM', 'LOW': 'LOW', 'UNKNOWN': 'UNKNOWN'},
                'ERROR': {'HIGH': 'UNKNOWN', 'MEDIUM': 'UNKNOWN', 'LOW': 'UNKNOWN', 'UNKNOWN': 'UNKNOWN'}
            }
            
            loan_risk_level = risk_matrix.get(regional_risk_level, {}).get(farm_vulnerability, 'UNKNOWN')
            
            # Calculate recommended actions based on risk level
            recommendations = []
            if loan_risk_level in ['EXTREME', 'HIGH']:
                recommendations.append('Consider term extension to reduce payment burden')
                recommendations.append('Monitor weather forecasts closely')
                recommendations.append('Suggest climate adaptation measures to the farmer')
            elif loan_risk_level == 'MEDIUM':
                recommendations.append('Regular monitoring of climate conditions')
                recommendations.append('Prepare contingency plan for term adjustments if needed')
            
            # Get any existing climate adjustments for this loan
            adjustments = loan.climate_adjustments.all().order_by('-adjustment_date')
            
            return {
                'success': True,
                'loan_risk_level': loan_risk_level,
                'regional_climate_risk': climate_risk['overall_risk'],
                'farm_vulnerability': vulnerability,
                'crop_risk': crop_risk,
                'recommendations': recommendations,
                'existing_adjustments': [
                    {
                        'type': adj.adjustment_type,
                        'date': adj.adjustment_date,
                        'climate_event': adj.climate_event,
                        'original_value': float(adj.original_value),
                        'adjusted_value': float(adj.adjusted_value)
                    } for adj in adjustments
                ]
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error assessing loan climate risk: {str(e)}'
            }
