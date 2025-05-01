"""
Loan models for the AgriFinance API.
Focused on essential data needed for mobile-first approach with AI-driven credit scoring.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum

from .base import Base

class LoanStatus(enum.Enum):
    """Loan status tracking throughout the lifecycle"""
    PENDING = "Pending"
    APPROVED = "Approved"
    DISBURSED = "Disbursed"
    REPAYING = "Repaying"
    COMPLETED = "Completed"
    DEFAULTED = "Defaulted"
    REJECTED = "Rejected"

class LoanType(enum.Enum):
    """Types of agricultural loans offered"""
    SEASONAL = "Seasonal"
    EQUIPMENT = "Equipment"
    INFRASTRUCTURE = "Infrastructure"
    EMERGENCY = "Emergency"
    EXPANSION = "Expansion"

class Loan(Base):
    """
    Loan model with essential information for financial tracking and AI credit scoring.
    """
    __tablename__ = "loans"
    
    id = Column(Integer, primary_key=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=False)
    loan_type = Column(Enum(LoanType), nullable=False)
    amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)  # Annual percentage rate
    term_months = Column(Integer, nullable=False)  # Loan duration in months
    status = Column(Enum(LoanStatus), default=LoanStatus.PENDING)
    application_date = Column(DateTime, default=datetime.utcnow)
    approval_date = Column(DateTime, nullable=True)
    disbursement_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    
    # For AI credit scoring and climate-adjusted loans
    credit_score = Column(Float, nullable=True)  # AI-generated score at time of application
    climate_risk_factor = Column(Float, nullable=True)  # Climate risk assessment at time of application
    
    # Relationships
    farmer = relationship("Farmer", back_populates="loans")
    payments = relationship("Payment", back_populates="loan", cascade="all, delete-orphan")
    
    def is_active(self):
        """Check if loan is currently active"""
        active_statuses = [LoanStatus.APPROVED, LoanStatus.DISBURSED, LoanStatus.REPAYING]
        return self.status in active_statuses
    
    def calculate_next_payment_date(self):
        """Calculate the next payment date based on disbursement date and payment frequency"""
        if not self.disbursement_date:
            return None
            
        # Simple monthly payment calculation
        # In a real app, this would be more sophisticated
        last_payment = max(self.payments, key=lambda p: p.payment_date) if self.payments else None
        
        if last_payment:
            return last_payment.payment_date + timedelta(days=30)
        else:
            return self.disbursement_date + timedelta(days=30)
    
    def calculate_remaining_balance(self):
        """Calculate remaining loan balance"""
        if not self.disbursement_date:
            return self.amount
            
        paid_amount = sum(payment.amount for payment in self.payments) if self.payments else 0
        return self.amount - paid_amount
    
    def to_dict(self):
        """Convert loan to dictionary for API responses"""
        return {
            "id": self.id,
            "farmer_id": self.farmer_id,
            "loan_type": self.loan_type.value if self.loan_type else None,
            "amount": self.amount,
            "interest_rate": self.interest_rate,
            "term_months": self.term_months,
            "status": self.status.value if self.status else None,
            "application_date": self.application_date.isoformat() if self.application_date else None,
            "approval_date": self.approval_date.isoformat() if self.approval_date else None,
            "disbursement_date": self.disbursement_date.isoformat() if self.disbursement_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "remaining_balance": self.calculate_remaining_balance(),
            "next_payment_date": self.calculate_next_payment_date().isoformat() if self.calculate_next_payment_date() else None,
            "credit_score": self.credit_score,
            "climate_risk_factor": self.climate_risk_factor
        }

class Payment(Base):
    """
    Payment model for tracking loan repayments.
    """
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    payment_method = Column(String(50), nullable=False)
    transaction_id = Column(String(100), nullable=True)
    
    # Relationships
    loan = relationship("Loan", back_populates="payments")
    
    def to_dict(self):
        """Convert payment to dictionary for API responses"""
        return {
            "id": self.id,
            "loan_id": self.loan_id,
            "amount": self.amount,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "payment_method": self.payment_method,
            "transaction_id": self.transaction_id
        }
