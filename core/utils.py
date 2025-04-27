import uuid
import datetime

def generate_loan_id():
    """
    Generate a unique loan ID with format: LN-{YEAR}-{RANDOM_ALPHANUMERIC}
    """
    current_year = datetime.datetime.now().year
    unique_part = uuid.uuid4().hex[:8].upper()
    return f"LN-{current_year}-{unique_part}"

def generate_farmer_id():
    """
    Generate a unique farmer ID with format: FR-{RANDOM_ALPHANUMERIC}
    """
    unique_part = uuid.uuid4().hex[:10].upper()
    return f"FR-{unique_part}"

def calculate_loan_schedule(loan_amount, interest_rate, term_months):
    """
    Calculate loan repayment schedule
    
    Args:
        loan_amount (float): The principal amount of the loan
        interest_rate (float): Annual interest rate (in percentage)
        term_months (int): Loan term in months
        
    Returns:
        list: A list of dictionaries containing payment details for each period
    """
    # Convert annual interest rate to monthly
    monthly_interest_rate = interest_rate / 100 / 12
    
    # Calculate monthly payment amount
    # Formula: P = A / ((1 - (1 + r)^-n) / r)
    # Where:
    # P = monthly payment
    # A = loan amount
    # r = monthly interest rate (in decimal)
    # n = number of months
    
    if monthly_interest_rate == 0:
        monthly_payment = loan_amount / term_months
    else:
        monthly_payment = loan_amount * (monthly_interest_rate / (1 - (1 + monthly_interest_rate) ** -term_months))
    
    # Create repayment schedule
    schedule = []
    remaining_balance = loan_amount
    
    for month in range(1, term_months + 1):
        interest_payment = remaining_balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment
        
        # Adjust for final payment to handle rounding errors
        if month == term_months:
            principal_payment += remaining_balance
            remaining_balance = 0
        
        payment = {
            'month': month,
            'payment_amount': round(monthly_payment, 2),
            'principal_payment': round(principal_payment, 2),
            'interest_payment': round(interest_payment, 2),
            'remaining_balance': round(remaining_balance, 2)
        }
        
        schedule.append(payment)
    
    return schedule

def calculate_loan_affordability(farmer, loan_product):
    """
    Calculate loan affordability based on farmer's repayment capacity
    
    Args:
        farmer (Farmer): The farmer object
        loan_product (LoanProduct): The loan product to analyze
        
    Returns:
        dict: A dictionary containing affordability metrics
    """
    # Get farmer's active loans
    active_loans = farmer.loans.filter(status__in=['APPROVED', 'DISBURSED', 'REPAYING'])
    
    # Calculate current debt service
    current_monthly_debt = 0
    for loan in active_loans:
        # Simple calculation - actual implementation would be more complex
        current_monthly_debt += (loan.amount / loan.term_months) * (1 + loan.interest_rate / 100 / 12)
    
    # Estimate income from farms (simplified)
    estimated_monthly_income = 0
    for farm in farmer.farms.all():
        # Simple estimation - actual implementation would consider crops, yields, etc.
        estimated_monthly_income += farm.area * 100  # Assumed 100 per hectare per month
    
    # Calculate debt-to-income ratio
    current_dti = current_monthly_debt / estimated_monthly_income if estimated_monthly_income > 0 else float('inf')
    
    # Calculate maximum affordable loan amount (assuming max DTI of 40%)
    max_dti = 0.4
    available_monthly_payment = (max_dti * estimated_monthly_income) - current_monthly_debt
    
    # Calculate maximum loan amount based on available payment
    monthly_interest_rate = loan_product.interest_rate / 100 / 12
    if monthly_interest_rate == 0:
        max_loan_amount = available_monthly_payment * loan_product.term_months
    else:
        max_loan_amount = available_monthly_payment * ((1 - (1 + monthly_interest_rate) ** -loan_product.term_months) / monthly_interest_rate)
    
    # Ensure max_loan_amount is within product limits
    max_loan_amount = min(max_loan_amount, loan_product.max_amount)
    max_loan_amount = max(max_loan_amount, 0)  # Ensure non-negative
    
    return {
        'current_monthly_debt': current_monthly_debt,
        'estimated_monthly_income': estimated_monthly_income,
        'current_dti': current_dti,
        'affordable_monthly_payment': available_monthly_payment,
        'max_loan_amount': max_loan_amount
    }
