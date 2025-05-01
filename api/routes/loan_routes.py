"""
Loan API routes for the AgriFinance mobile app.
Provides endpoints for loan applications, management, and repayments.
"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime, timedelta

from api.models import Loan, LoanType, LoanStatus, Payment, Farmer
from api import db

# Configure logging
logger = logging.getLogger('agrifinance_api.loan')

# Create blueprint
loan_api = Blueprint('loan_api', __name__)

@loan_api.route('/', methods=['GET'])
def get_loans():
    """Get all loans or filter by query parameters"""
    try:
        # Support filtering by various parameters
        farmer_id = request.args.get('farmer_id', type=int)
        status = request.args.get('status')
        loan_type = request.args.get('type')
        
        query = db.session.query(Loan)
        
        if farmer_id:
            query = query.filter(Loan.farmer_id == farmer_id)
        
        if status:
            try:
                status_enum = LoanStatus(status)
                query = query.filter(Loan.status == status_enum)
            except ValueError:
                return jsonify({"error": f"Invalid loan status: {status}"}), 400
        
        if loan_type:
            try:
                loan_type_enum = LoanType(loan_type)
                query = query.filter(Loan.loan_type == loan_type_enum)
            except ValueError:
                return jsonify({"error": f"Invalid loan type: {loan_type}"}), 400
        
        loans = query.all()
        return jsonify([loan.to_dict() for loan in loans])
        
    except Exception as e:
        logger.error(f"Error getting loans: {str(e)}")
        return jsonify({"error": str(e)}), 500

@loan_api.route('/<int:loan_id>', methods=['GET'])
def get_loan(loan_id):
    """Get a specific loan by ID"""
    try:
        loan = db.session.get(Loan, loan_id)
        if not loan:
            return jsonify({"error": "Loan not found"}), 404
            
        return jsonify(loan.to_dict())
        
    except Exception as e:
        logger.error(f"Error getting loan {loan_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@loan_api.route('/', methods=['POST'])
def create_loan():
    """Create a new loan application"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['farmer_id', 'loan_type', 'amount', 'interest_rate', 'term_months']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if farmer exists
        farmer = db.session.get(Farmer, data['farmer_id'])
        if not farmer:
            return jsonify({"error": f"Farmer with ID {data['farmer_id']} not found"}), 404
        
        # Parse loan type
        try:
            loan_type = LoanType(data['loan_type'])
        except ValueError:
            return jsonify({"error": f"Invalid loan type: {data['loan_type']}"}), 400
        
        # Create new loan application
        loan = Loan(
            farmer_id=data['farmer_id'],
            loan_type=loan_type,
            amount=data['amount'],
            interest_rate=data['interest_rate'],
            term_months=data['term_months'],
            status=LoanStatus.PENDING,
            application_date=datetime.utcnow(),
            credit_score=data.get('credit_score'),
            climate_risk_factor=data.get('climate_risk_factor')
        )
        
        db.session.add(loan)
        db.session.commit()
        
        return jsonify(loan.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error creating loan: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@loan_api.route('/<int:loan_id>/status', methods=['PUT'])
def update_loan_status(loan_id):
    """Update the status of a loan"""
    try:
        loan = db.session.get(Loan, loan_id)
        if not loan:
            return jsonify({"error": "Loan not found"}), 404
            
        data = request.json
        
        if 'status' not in data:
            return jsonify({"error": "Missing required field: status"}), 400
            
        # Parse status
        try:
            new_status = LoanStatus(data['status'])
        except ValueError:
            return jsonify({"error": f"Invalid loan status: {data['status']}"}), 400
            
        # Update status and related fields
        old_status = loan.status
        loan.status = new_status
        
        if new_status == LoanStatus.APPROVED and old_status == LoanStatus.PENDING:
            loan.approval_date = datetime.utcnow()
            
        elif new_status == LoanStatus.DISBURSED and old_status == LoanStatus.APPROVED:
            loan.disbursement_date = datetime.utcnow()
            # Set due date based on term
            loan.due_date = loan.disbursement_date + timedelta(days=30 * loan.term_months)
            
        elif new_status == LoanStatus.COMPLETED:
            # Verify all payments have been made
            remaining_balance = loan.calculate_remaining_balance()
            if remaining_balance > 0:
                return jsonify({"error": f"Cannot mark loan as completed. Remaining balance: {remaining_balance}"}), 400
        
        db.session.commit()
        
        return jsonify(loan.to_dict())
        
    except Exception as e:
        logger.error(f"Error updating loan status for loan {loan_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@loan_api.route('/<int:loan_id>/payments', methods=['GET'])
def get_loan_payments(loan_id):
    """Get all payments for a loan"""
    try:
        loan = db.session.get(Loan, loan_id)
        if not loan:
            return jsonify({"error": "Loan not found"}), 404
            
        payments = [payment.to_dict() for payment in loan.payments]
        
        return jsonify({
            "loan_id": loan_id,
            "total_amount": loan.amount,
            "total_paid": sum(payment['amount'] for payment in payments),
            "remaining_balance": loan.calculate_remaining_balance(),
            "payments": payments
        })
        
    except Exception as e:
        logger.error(f"Error getting payments for loan {loan_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@loan_api.route('/<int:loan_id>/payments', methods=['POST'])
def add_loan_payment(loan_id):
    """Add a new payment to a loan"""
    try:
        loan = db.session.get(Loan, loan_id)
        if not loan:
            return jsonify({"error": "Loan not found"}), 404
            
        # Verify loan is in a status that can accept payments
        if loan.status not in [LoanStatus.DISBURSED, LoanStatus.REPAYING]:
            return jsonify({"error": f"Cannot add payment to loan with status: {loan.status.value}"}), 400
            
        data = request.json
        
        # Validate required fields
        required_fields = ['amount', 'payment_method']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
                
        # Create new payment
        payment = Payment(
            loan_id=loan_id,
            amount=data['amount'],
            payment_date=datetime.utcnow(),
            payment_method=data['payment_method'],
            transaction_id=data.get('transaction_id')
        )
        
        db.session.add(payment)
        
        # Update loan status if this is the first payment
        if loan.status == LoanStatus.DISBURSED:
            loan.status = LoanStatus.REPAYING
            
        # Check if loan is now fully paid
        remaining_balance = loan.calculate_remaining_balance() - data['amount']
        if remaining_balance <= 0:
            loan.status = LoanStatus.COMPLETED
            
        db.session.commit()
        
        return jsonify({
            "payment": payment.to_dict(),
            "remaining_balance": remaining_balance,
            "loan_status": loan.status.value
        }), 201
        
    except Exception as e:
        logger.error(f"Error adding payment to loan {loan_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@loan_api.route('/farmer/<int:farmer_id>/summary', methods=['GET'])
def get_farmer_loans_summary(farmer_id):
    """Get a summary of all loans for a farmer"""
    try:
        # Check if farmer exists
        farmer = db.session.get(Farmer, farmer_id)
        if not farmer:
            return jsonify({"error": f"Farmer with ID {farmer_id} not found"}), 404
            
        loans = db.session.query(Loan).filter(Loan.farmer_id == farmer_id).all()
        
        # Calculate summary statistics
        total_loans = len(loans)
        active_loans = sum(1 for loan in loans if loan.is_active())
        completed_loans = sum(1 for loan in loans if loan.status == LoanStatus.COMPLETED)
        defaulted_loans = sum(1 for loan in loans if loan.status == LoanStatus.DEFAULTED)
        
        total_borrowed = sum(loan.amount for loan in loans)
        total_active = sum(loan.amount for loan in loans if loan.is_active())
        total_repaid = sum(
            sum(payment.amount for payment in loan.payments) if loan.payments else 0
            for loan in loans
        )
        
        # Calculate status distribution
        status_counts = {}
        for loan in loans:
            status = loan.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
        # Calculate loan type distribution
        type_counts = {}
        for loan in loans:
            loan_type = loan.loan_type.value
            type_counts[loan_type] = type_counts.get(loan_type, 0) + 1
        
        # Get upcoming payments
        upcoming_payments = []
        for loan in loans:
            if not loan.is_active():
                continue
                
            next_payment_date = loan.calculate_next_payment_date()
            if next_payment_date:
                # Estimate payment amount (simple calculation for demo)
                monthly_payment = loan.amount / loan.term_months
                
                upcoming_payments.append({
                    "loan_id": loan.id,
                    "loan_type": loan.loan_type.value,
                    "payment_date": next_payment_date.isoformat(),
                    "estimated_amount": round(monthly_payment, 2),
                    "days_remaining": (next_payment_date - datetime.utcnow()).days
                })
        
        # Sort by date
        upcoming_payments.sort(key=lambda x: x["payment_date"])
        
        return jsonify({
            "farmer_id": farmer_id,
            "summary": {
                "total_loans": total_loans,
                "active_loans": active_loans,
                "completed_loans": completed_loans,
                "defaulted_loans": defaulted_loans,
                "total_borrowed": total_borrowed,
                "total_active": total_active,
                "total_repaid": total_repaid,
                "remaining_balance": total_borrowed - total_repaid
            },
            "status_distribution": [{"status": status, "count": count} for status, count in status_counts.items()],
            "type_distribution": [{"type": loan_type, "count": count} for loan_type, count in type_counts.items()],
            "upcoming_payments": upcoming_payments,
            "loans": [loan.to_dict() for loan in loans]
        })
        
    except Exception as e:
        logger.error(f"Error getting loans summary for farmer {farmer_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500
