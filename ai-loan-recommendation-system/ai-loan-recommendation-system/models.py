"""
SQLAlchemy Database Models for AI-Based Loan Detection and Recommendation System.
Supports SQLite (default) and MySQL via DATABASE_URL configuration.
"""

from datetime import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), default="user", nullable=False)  # 'user' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    applications = db.relationship("LoanApplication", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"


class LoanApplication(db.Model):
    __tablename__ = "loan_applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    
    # 1. Personal & Contact
    full_name = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    
    # 2. Location
    state = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=False)
    city_village = db.Column(db.String(100), nullable=False)
    
    # 3. Employment & Financial
    occupation = db.Column(db.String(100), nullable=False)
    monthly_income = db.Column(db.Float, nullable=False)
    annual_income = db.Column(db.Float, nullable=False)
    employment_type = db.Column(db.String(100), nullable=False)
    company_name = db.Column(db.String(150), nullable=True)
    credit_score = db.Column(db.Integer, nullable=False, default=700)
    existing_loans = db.Column(db.Integer, default=0)
    existing_emi = db.Column(db.Float, default=0.0)
    
    # 4. Loan Requirements
    loan_amount = db.Column(db.Float, nullable=False)
    loan_purpose = db.Column(db.String(200), nullable=False)
    loan_tenure = db.Column(db.Integer, nullable=False)  # in months
    
    # 5. Profile & Demographics
    education_status = db.Column(db.String(100), nullable=False)
    applicant_persona = db.Column(db.String(50), nullable=False)  # Student/Working/Business/Farmer
    
    # 6. Asset & Activity
    house_ownership = db.Column(db.String(50), nullable=False)
    land_ownership = db.Column(db.String(20), nullable=False)  # Yes/No
    agricultural_activity = db.Column(db.String(100), default="None")
    business_type = db.Column(db.String(100), default="None")
    vehicle_requirement = db.Column(db.String(100), default="None")
    collateral_availability = db.Column(db.String(100), default="None")
    bank_account_status = db.Column(db.String(100), default="Active Savings Account")

    # 7. AI Prediction & Eligibility Output
    top_category = db.Column(db.String(100), nullable=True)
    top_score = db.Column(db.Integer, nullable=True)
    second_category = db.Column(db.String(100), nullable=True)
    second_score = db.Column(db.Integer, nullable=True)
    third_category = db.Column(db.String(100), nullable=True)
    third_score = db.Column(db.Integer, nullable=True)
    all_scores_json = db.Column(db.Text, nullable=True)
    
    eligibility_status = db.Column(db.String(50), nullable=True)  # Likely Eligible, Requires Further Review, High Risk
    eligibility_score = db.Column(db.Integer, nullable=True)
    eligibility_details_json = db.Column(db.Text, nullable=True)
    recommended_amount_min = db.Column(db.Float, nullable=True)
    recommended_amount_max = db.Column(db.Float, nullable=True)
    suggested_tenure = db.Column(db.String(50), nullable=True)
    reason_text = db.Column(db.Text, nullable=True)
    
    # Application lifecycle
    status = db.Column(db.String(50), default="Submitted")  # Submitted, Under Review, Verified, Approved, Rejected
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    documents = db.relationship("ApplicationDocument", backref="application", lazy=True, cascade="all, delete-orphan")

    def get_all_scores(self):
        try:
            return json.loads(self.all_scores_json) if self.all_scores_json else {}
        except Exception:
            return {}

    def get_eligibility_details(self):
        try:
            return json.loads(self.eligibility_details_json) if self.eligibility_details_json else {}
        except Exception:
            return {}


class ApplicationDocument(db.Model):
    __tablename__ = "application_documents"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("loan_applications.id"), nullable=False)
    
    doc_name = db.Column(db.String(150), nullable=False)
    doc_category = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    mime_type = db.Column(db.String(100), nullable=True)
    is_camera_scan = db.Column(db.Boolean, default=False)
    
    # Status: 'Pending Verification', 'Verified', 'Rejected'
    verification_status = db.Column(db.String(50), default="Pending Verification")
    rejection_reason = db.Column(db.Text, nullable=True)
    verified_by = db.Column(db.String(100), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LoanScheme(db.Model):
    __tablename__ = "loan_schemes"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    bank_name = db.Column(db.String(150), nullable=False)
    scheme_name = db.Column(db.String(200), nullable=False)
    interest_rate_min = db.Column(db.Float, nullable=False)
    interest_rate_max = db.Column(db.Float, nullable=False)
    max_amount = db.Column(db.Float, nullable=False)
    max_tenure_months = db.Column(db.Integer, nullable=False)
    processing_fee = db.Column(db.String(100), nullable=False)
    eligibility_summary = db.Column(db.Text, nullable=False)
    required_docs_summary = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
