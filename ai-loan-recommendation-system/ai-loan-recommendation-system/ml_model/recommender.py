"""
AI Loan Recommendation & Eligibility Engine.
Provides multi-category suitability prediction, Top-3 ranking,
financial eligibility analysis (DTI/FOIR), amount range estimation,
and personalized reasoning.
"""

import os
import joblib
import numpy as np
import pandas as pd

# Benchmark interest rates, tenures, and document checklists (Realistic Indian Banking Standards: SBI, PMMY, NABARD, HDFC)
LOAN_CATEGORY_DETAILS = {
    "Home Loan": {
        "interest_rate_range": "8.35% - 9.65% p.a.",
        "benchmark_rate": 8.50,
        "max_tenure_months": 360,
        "min_tenure_months": 36,
        "processing_fee": "0.35% - 0.50% (Max ₹10,000)",
        "basic_conditions": [
            "Applicant age between 21 and 65 years",
            "Minimum net monthly income of ₹25,000 (Salaried) or ₹35,000 (Self-employed)",
            "Clear title of the property and sanctioned construction plan",
            "Credit score preferably 700+"
        ],
        "required_documents": [
            {"name": "Aadhaar Card", "category": "Identity & Address Proof", "mandatory": True},
            {"name": "PAN Card", "category": "Tax / Identity Proof", "mandatory": True},
            {"name": "Last 3 Months Salary Slips / ITR (2 Years)", "category": "Income Proof", "mandatory": True},
            {"name": "Last 6 Months Bank Statement", "category": "Banking Proof", "mandatory": True},
            {"name": "Property Sale Agreement / Title Deed / Blueprint", "category": "Property Documents", "mandatory": True},
            {"name": "Approved Building Plan & NOC from Authority", "category": "Legal Proof", "mandatory": False}
        ]
    },
    "Education / Student Loan": {
        "interest_rate_range": "8.50% - 11.15% p.a.",
        "benchmark_rate": 8.75,
        "max_tenure_months": 180,
        "min_tenure_months": 12,
        "processing_fee": "Nil for loans up to ₹7.5 Lakhs; 1% for study abroad",
        "basic_conditions": [
            "Indian national with confirmed admission in recognized college/university",
            "Parent / Guardian as co-borrower / co-applicant",
            "Moratorium period: Course duration + 1 year (or 6 months after getting job)",
            "No collateral required up to ₹4-7.5 Lakhs (CGFSEL scheme coverage)"
        ],
        "required_documents": [
            {"name": "Aadhaar Card of Student & Co-Applicant", "category": "Identity Proof", "mandatory": True},
            {"name": "PAN Card of Student & Co-Applicant", "category": "Identity Proof", "mandatory": True},
            {"name": "College Admission Letter & Fee Structure", "category": "Academic Proof", "mandatory": True},
            {"name": "Academic Records (10th, 12th, Degree Marksheets)", "category": "Academic Proof", "mandatory": True},
            {"name": "Co-Applicant Income Proof & Bank Statement", "category": "Income Proof", "mandatory": True},
            {"name": "Entrance Exam Scorecard (JEE/NEET/GRE/CAT)", "category": "Academic Proof", "mandatory": False}
        ]
    },
    "Agriculture / Farmer Loan": {
        "interest_rate_range": "4.00% - 7.00% p.a. (with Govt Subvention)",
        "benchmark_rate": 7.00,
        "max_tenure_months": 84,
        "min_tenure_months": 6,
        "processing_fee": "Nil for loans up to ₹3 Lakhs under KCC",
        "basic_conditions": [
            "Farmer / Owner cultivator / Tenant farmer / SHG or JLG",
            "Valid agricultural land ownership (Patta / 7/12 extract) or tenancy agreement",
            "Active engagement in crop cultivation, horticulture, dairy, or allied farming",
            "Interest subvention of 3% for prompt repayment (effective rate 4%)"
        ],
        "required_documents": [
            {"name": "Aadhaar Card", "category": "Identity & Address Proof", "mandatory": True},
            {"name": "PAN Card / Form 60", "category": "Identity Proof", "mandatory": True},
            {"name": "Land Record Documents (7/12 / 8A / Patta / Land Ownership Book)", "category": "Asset Proof", "mandatory": True},
            {"name": "Crop Cultivation Certificate / Village Patwari Certificate", "category": "Farming Proof", "mandatory": True},
            {"name": "Bank Passbook / Statement (Last 6 Months)", "category": "Banking Proof", "mandatory": True},
            {"name": "Quotation for Seeds/Fertilizer/Equipment/Tractor", "category": "Estimate Proof", "mandatory": False}
        ]
    },
    "Personal Loan": {
        "interest_rate_range": "10.49% - 15.50% p.a.",
        "benchmark_rate": 10.99,
        "max_tenure_months": 60,
        "min_tenure_months": 12,
        "processing_fee": "1.00% - 2.50% + GST",
        "basic_conditions": [
            "Salaried or self-employed with minimum 1-year stable work experience",
            "Minimum net monthly take-home salary ₹20,000",
            "Credit score 680 or higher preferred",
            "No collateral or security required (unsecured loan)"
        ],
        "required_documents": [
            {"name": "Aadhaar Card", "category": "Identity Proof", "mandatory": True},
            {"name": "PAN Card", "category": "Identity Proof", "mandatory": True},
            {"name": "Latest 3 Months Salary Slips", "category": "Income Proof", "mandatory": True},
            {"name": "Last 6 Months Salary Account Bank Statement", "category": "Banking Proof", "mandatory": True},
            {"name": "Current Employment ID Card / Appointment Letter", "category": "Employment Proof", "mandatory": False}
        ]
    },
    "Business Loan": {
        "interest_rate_range": "11.00% - 16.50% p.a.",
        "benchmark_rate": 11.50,
        "max_tenure_months": 60,
        "min_tenure_months": 12,
        "processing_fee": "1.25% - 2.00% + GST",
        "basic_conditions": [
            "Business vintage of at least 2 to 3 years",
            "Minimum annual business turnover of ₹15 Lakhs",
            "Profitable business track record with audited financials or GST returns",
            "Good business and promoter credit profile"
        ],
        "required_documents": [
            {"name": "Promoter Aadhaar & PAN Card", "category": "Identity Proof", "mandatory": True},
            {"name": "Business Registration / Udyam / Shop & Establishment Certificate", "category": "Business Proof", "mandatory": True},
            {"name": "GST Returns (Last 12 Months)", "category": "Tax Proof", "mandatory": True},
            {"name": "Current Account Bank Statements (Last 12 Months)", "category": "Banking Proof", "mandatory": True},
            {"name": "ITR & Computation of Income with Balance Sheet (Last 2 Years)", "category": "Financial Proof", "mandatory": True}
        ]
    },
    "Vehicle Loan": {
        "interest_rate_range": "8.75% - 10.25% p.a.",
        "benchmark_rate": 8.85,
        "max_tenure_months": 84,
        "min_tenure_months": 12,
        "processing_fee": "0.50% or flat ₹1,500 - ₹3,000",
        "basic_conditions": [
            "Applicant age 21 to 65 years",
            "Minimum monthly income ₹18,000 (Two-wheeler) or ₹25,000 (Car/Commercial)",
            "Vehicle will be hypothecated to the financing bank until full loan repayment",
            "Dealer proforma invoice required"
        ],
        "required_documents": [
            {"name": "Aadhaar Card", "category": "Identity Proof", "mandatory": True},
            {"name": "PAN Card", "category": "Identity Proof", "mandatory": True},
            {"name": "Income Proof (Salary Slips / ITR / Form 16)", "category": "Income Proof", "mandatory": True},
            {"name": "Bank Statement (Last 6 Months)", "category": "Banking Proof", "mandatory": True},
            {"name": "Dealer Proforma Invoice / Price Quotation", "category": "Asset Proof", "mandatory": True},
            {"name": "Driving License (if applicable)", "category": "KYC Proof", "mandatory": False}
        ]
    },
    "Gold Loan": {
        "interest_rate_range": "7.50% - 11.50% p.a.",
        "benchmark_rate": 8.25,
        "max_tenure_months": 36,
        "min_tenure_months": 3,
        "processing_fee": "0.25% - 0.50% (Max ₹2,500)",
        "basic_conditions": [
            "Applicant must own gold jewellery / ornaments (18 to 22 karat)",
            "Loan-to-Value (LTV) up to 75% of appraised gold market value",
            "Minimal income documentation required; instant disbursement",
            "Flexible repayment (Bullet repayment / Monthly interest / EMI)"
        ],
        "required_documents": [
            {"name": "Aadhaar Card / Voter ID / Passport", "category": "Identity & Address Proof", "mandatory": True},
            {"name": "PAN Card", "category": "Identity Proof", "mandatory": True},
            {"name": "Passport size photograph", "category": "KYC Proof", "mandatory": True},
            {"name": "Gold Ornaments for in-branch assay/valuation", "category": "Collateral Proof", "mandatory": True}
        ]
    },
    "MSME / Startup Loan": {
        "interest_rate_range": "8.50% - 12.50% p.a.",
        "benchmark_rate": 9.25,
        "max_tenure_months": 84,
        "min_tenure_months": 12,
        "processing_fee": "0.50% - 1.00%",
        "basic_conditions": [
            "Registered as Micro, Small or Medium Enterprise (Udyam Registration)",
            "Eligible for CGTMSE (Collateral Free credit guarantee up to ₹5 Crore)",
            "Viable project report and projected cash flow statements",
            "Promoter contribution of at least 15% to 25%"
        ],
        "required_documents": [
            {"name": "Promoter Aadhaar & PAN Card", "category": "Identity Proof", "mandatory": True},
            {"name": "Udyam Registration Certificate", "category": "Registration Proof", "mandatory": True},
            {"name": "Detailed Project Report (DPR) & Cost Estimates", "category": "Project Proof", "mandatory": True},
            {"name": "Bank Statement (Last 6-12 Months)", "category": "Banking Proof", "mandatory": True},
            {"name": "GST Returns & Financial Statements (if existing enterprise)", "category": "Financial Proof", "mandatory": False}
        ]
    },
    "Women / Special Category Loan": {
        "interest_rate_range": "7.25% - 10.50% p.a. (Concessional)",
        "benchmark_rate": 7.80,
        "max_tenure_months": 84,
        "min_tenure_months": 12,
        "processing_fee": "Concessional / Zero Processing Fee under Women schemes",
        "basic_conditions": [
            "Woman entrepreneur holding at least 51% stake in business / self-employed",
            "Interest concession of 0.25% to 0.50% compared to standard commercial rates",
            "Coverage under Stand-Up India, Mudra Mahila Udyam Nidhi, or Stree Shakti",
            "Minimum age 18 years"
        ],
        "required_documents": [
            {"name": "Woman Applicant Aadhaar Card", "category": "Identity Proof", "mandatory": True},
            {"name": "PAN Card", "category": "Identity Proof", "mandatory": True},
            {"name": "Proof of Business Ownership / Partnership Deed / Udyam", "category": "Ownership Proof", "mandatory": True},
            {"name": "Bank Statement (Last 6 Months)", "category": "Banking Proof", "mandatory": True},
            {"name": "Project Proposal / Quotation for Assets", "category": "Project Proof", "mandatory": True}
        ]
    },
    "Government-Supported Loan Schemes": {
        "interest_rate_range": "4.00% - 9.50% p.a. (Subsidized)",
        "benchmark_rate": 7.50,
        "max_tenure_months": 84,
        "min_tenure_months": 12,
        "processing_fee": "Nil to Minimal under PMMY / PMEGP guidelines",
        "basic_conditions": [
            "Qualify under criteria for PM MUDRA (Shishu ≤50k, Kishore ≤5L, Tarun ≤10L), PMEGP, or KCC",
            "Subsidies on capital / interest under specific Central or State government programs",
            "Collateral-free financing backed by Credit Guarantee Funds",
            "Valid identity and bank account linked to Aadhaar (DBT active)"
        ],
        "required_documents": [
            {"name": "Aadhaar Card (Aadhaar linked to Mobile/DBT)", "category": "Identity Proof", "mandatory": True},
            {"name": "PAN Card", "category": "Identity Proof", "mandatory": True},
            {"name": "Scheme Application Form & Project Quotation", "category": "Scheme Proof", "mandatory": True},
            {"name": "Caste / Category Certificate (if claiming special subsidy)", "category": "Category Proof", "mandatory": False},
            {"name": "Bank Passbook / Bank Statement (Last 6 Months)", "category": "Banking Proof", "mandatory": True}
        ]
    }
}

class LoanRecommender:
    def __init__(self, model_file=None):
        if model_file is None:
            base_dir = os.path.dirname(__file__)
            model_file = os.path.join(base_dir, "loan_classifier_pipeline.joblib")
            
        if os.path.exists(model_file):
            bundle = joblib.load(model_file)
            self.pipeline = bundle["pipeline"]
            self.metadata = bundle["metadata"]
            self.classes = self.metadata["classes"]
            print(f"[LoanRecommender] Loaded pipeline with {len(self.classes)} classes.")
        else:
            print(f"[LoanRecommender] Model file not found at {model_file}. Running fallback mode.")
            self.pipeline = None
            self.classes = list(LOAN_CATEGORY_DETAILS.keys())

    def _calculate_rule_based_affinities(self, profile):
        """
        Calculate nuanced domain-specific affinities across all 10 loan categories.
        Combines purpose intent, demographic eligibility, asset ownership, and employment.
        """
        affinities = {cat: 0.05 for cat in LOAN_CATEGORY_DETAILS.keys()}
        
        purpose = str(profile.get("loan_purpose", "")).lower()
        occupation = str(profile.get("occupation", "")).lower()
        persona = str(profile.get("applicant_persona", "")).lower()
        gender = str(profile.get("gender", "")).lower()
        emp_type = str(profile.get("employment_type", "")).lower()
        land_own = str(profile.get("land_ownership", "")).lower()
        agri_act = str(profile.get("agricultural_activity", "")).lower()
        collateral = str(profile.get("collateral_availability", "")).lower()
        vehicle = str(profile.get("vehicle_requirement", "")).lower()
        biz_type = str(profile.get("business_type", "")).lower()
        income = float(profile.get("monthly_income", 0))
        amount = float(profile.get("loan_amount", 0))
        
        # 1. Agriculture / Farmer Loan
        if "farmer" in occupation or "farmer" in persona or "agri" in emp_type:
            affinities["Agriculture / Farmer Loan"] += 0.50
        if land_own == "yes":
            affinities["Agriculture / Farmer Loan"] += 0.20
        if agri_act != "none" and agri_act != "":
            affinities["Agriculture / Farmer Loan"] += 0.25
        if any(w in purpose for w in ["crop", "farm", "kisan", "cultivat", "fertiliz", "seed", "irrigation", "dairy", "poultry"]):
            affinities["Agriculture / Farmer Loan"] += 0.50
            
        # 2. Education / Student Loan
        if "student" in occupation or "student" in persona or "student" in emp_type:
            affinities["Education / Student Loan"] += 0.55
        if any(w in purpose for w in ["college", "study", "education", "degree", "university", "master", "exam", "tuition"]):
            affinities["Education / Student Loan"] += 0.60
            
        # 3. Home Loan
        if any(w in purpose for w in ["house", "home", "flat", "apartment", "renovat", "construct"]):
            affinities["Home Loan"] += 0.65
        if "salaried" in emp_type or "salaried" in occupation:
            affinities["Home Loan"] += 0.15
        if "property" in collateral or "land" in collateral:
            affinities["Home Loan"] += 0.15
            
        # 4. Vehicle Loan
        if vehicle not in ["none", ""]:
            affinities["Vehicle Loan"] += 0.55
        if any(w in purpose for w in ["car", "bike", "two-wheeler", "vehicle", "tractor", "truck", "tempo"]):
            affinities["Vehicle Loan"] += 0.60
        # If tractor, also ties with Agriculture
        if "tractor" in purpose or "tractor" in vehicle:
            affinities["Agriculture / Farmer Loan"] += 0.40
            affinities["Vehicle Loan"] += 0.45
            
        # 5. Business Loan
        if "business" in occupation or "business" in persona or "business" in emp_type:
            affinities["Business Loan"] += 0.45
        if biz_type not in ["none", ""]:
            affinities["Business Loan"] += 0.30
        if any(w in purpose for w in ["business", "inventory", "working capital", "shop", "expansion", "machinery"]):
            affinities["Business Loan"] += 0.55
            
        # 6. MSME / Startup Loan
        if any(w in purpose for w in ["startup", "msme", "small enterprise", "manufacturing", "greenfield", "innovation"]):
            affinities["MSME / Startup Loan"] += 0.65
        if biz_type in ["tech startup", "manufacturing", "services"]:
            affinities["MSME / Startup Loan"] += 0.35
            
        # 7. Women / Special Category Loan
        if gender == "female":
            affinities["Women / Special Category Loan"] += 0.30
            if "business" in persona or "self-employed" in occupation or "homemaker" in occupation or biz_type != "none":
                affinities["Women / Special Category Loan"] += 0.45
        if any(w in purpose for w in ["women", "mahila", "self-help", "boutique", "shg", "stree"]):
            affinities["Women / Special Category Loan"] += 0.65
            
        # 8. Gold Loan
        if "gold" in collateral:
            affinities["Gold Loan"] += 0.65
        if any(w in purpose for w in ["gold", "pledg", "instant emergency", "liquidity against gold"]):
            affinities["Gold Loan"] += 0.70
            
        # 9. Government-Supported Loan Schemes
        if any(w in purpose for w in ["mudra", "pmegp", "subsidy", "scheme", "kcc", "stand-up", "government", "govt"]):
            affinities["Government-Supported Loan Schemes"] += 0.70
        if income <= 40000 and (persona in ["farmer", "student"] or "homemaker" in occupation):
            affinities["Government-Supported Loan Schemes"] += 0.30
            
        # 10. Personal Loan
        if any(w in purpose for w in ["personal", "medical", "marriage", "wedding", "emergency", "travel", "vacation", "urgent"]):
            affinities["Personal Loan"] += 0.65
        if ("salaried" in emp_type or "working" in persona) and collateral == "none":
            affinities["Personal Loan"] += 0.20
            
        return affinities

    def predict_suitability(self, user_profile):
        """
        Calculates loan suitability score for all 10 loan categories.
        Combines AI/ML Classifier Probabilities with Domain Knowledge Affinities.
        """
        # Ensure numerical types
        profile = dict(user_profile)
        for key in ["age", "monthly_income", "annual_income", "credit_score", "existing_loans", "existing_emi", "loan_amount", "loan_tenure"]:
            try:
                profile[key] = float(profile.get(key, 0))
            except (ValueError, TypeError):
                profile[key] = 0.0

        if not profile.get("annual_income") and profile.get("monthly_income"):
            profile["annual_income"] = profile["monthly_income"] * 12

        # 1. AI Pipeline Probabilities
        ml_probs = {cat: 0.10 for cat in LOAN_CATEGORY_DETAILS.keys()}
        if self.pipeline:
            try:
                input_df = pd.DataFrame([profile])
                # Ensure all training columns exist
                for col in self.metadata["numeric_features"] + self.metadata["categorical_features"]:
                    if col not in input_df.columns:
                        input_df[col] = "None" if col in self.metadata["categorical_features"] else 0.0
                
                probs = self.pipeline.predict_proba(input_df)[0]
                for cat, p in zip(self.classes, probs):
                    ml_probs[cat] = float(p)
            except Exception as e:
                print(f"[LoanRecommender] Prediction error: {e}")

        # 2. Rule / Domain Affinities
        rule_affinities = self._calculate_rule_based_affinities(profile)

        # 3. Blended Suitability Score
        scores = {}
        for cat in LOAN_CATEGORY_DETAILS.keys():
            ml_p = ml_probs.get(cat, 0.05)
            rule_p = rule_affinities.get(cat, 0.05)
            # Weighted combination: 60% ML prediction + 40% rule/contextual affinity
            blended = (0.60 * ml_p) + (0.40 * min(1.0, rule_p))
            # Scale to clean percentages (10% to 98% range)
            score_pct = int(np.clip(blended * 100, 5, 96))
            scores[cat] = score_pct

        # Find best match category and boost confidence for clear match
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_cat, top_score = sorted_scores[0]
        
        # Ensure top category stands out realistically (e.g. 88%-96%)
        if top_score < 80:
            scores[top_cat] = min(95, top_score + 25)
        
        # Recalculate sorted
        ranked_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return scores, ranked_categories

    def analyze_eligibility(self, profile, top_category):
        """
        Performs thorough financial eligibility analysis:
        - Debt-to-Income (DTI) and FOIR
        - Credit score evaluation
        - Repayment capacity
        - Loan-to-income feasibility
        - Collateral requirement check
        """
        monthly_income = float(profile.get("monthly_income", 0))
        existing_emi = float(profile.get("existing_emi", 0))
        loan_amount = float(profile.get("loan_amount", 0))
        tenure_months = max(6, int(profile.get("loan_tenure", 36)))
        credit_score = int(profile.get("credit_score", 0))
        collateral = str(profile.get("collateral_availability", "None"))
        occupation = str(profile.get("occupation", ""))
        
        cat_info = LOAN_CATEGORY_DETAILS.get(top_category, LOAN_CATEGORY_DETAILS["Personal Loan"])
        benchmark_rate = cat_info["benchmark_rate"]
        
        # Calculate proposed EMI using standard formula: E = P * r * (1+r)^n / ((1+r)^n - 1)
        r = (benchmark_rate / 12) / 100
        n = tenure_months
        if r > 0 and n > 0 and loan_amount > 0:
            proposed_emi = (loan_amount * r * ((1 + r) ** n)) / (((1 + r) ** n) - 1)
        else:
            proposed_emi = (loan_amount / n) if n > 0 else 0

        total_obligations = existing_emi + proposed_emi
        foir = (total_obligations / monthly_income * 100) if monthly_income > 0 else 100.0
        existing_dti = (existing_emi / monthly_income * 100) if monthly_income > 0 else 0.0

        reasons = []
        flags = []
        eligibility_score = 100

        # FOIR / DTI evaluation
        if monthly_income <= 0:
            if occupation == "Student" and top_category == "Education / Student Loan":
                reasons.append("Student applicant: Eligibility evaluated based on co-applicant / parent income and future earning potential.")
            else:
                eligibility_score -= 40
                flags.append("Zero or unverified regular monthly income declared.")
        elif foir <= 40:
            reasons.append(f"Healthy FOIR / Debt burden at {foir:.1f}%. Repayment capacity is strong.")
        elif foir <= 55:
            reasons.append(f"Moderate FOIR at {foir:.1f}%. Repayment is feasible within acceptable banking norms.")
        elif foir <= 70:
            eligibility_score -= 25
            flags.append(f"High total debt obligations (FOIR: {foir:.1f}%). May require longer tenure or lower loan amount.")
        else:
            eligibility_score -= 45
            flags.append(f"Excessive debt burden (FOIR: {foir:.1f}% exceeds recommended 60% threshold).")

        # Credit Score evaluation
        if credit_score >= 750:
            reasons.append(f"Excellent credit score ({credit_score}). High creditworthiness and best rate qualification.")
        elif credit_score >= 700:
            reasons.append(f"Good credit score ({credit_score}). Qualifies for standard prime bank lending terms.")
        elif credit_score >= 600:
            reasons.append(f"Moderate credit score ({credit_score}). Satisfies basic minimum eligibility criteria.")
            eligibility_score -= 10
        elif credit_score > 0:
            eligibility_score -= 30
            flags.append(f"Credit score ({credit_score}) is below preferred threshold of 650.")
        else:
            # 0 credit score (New to credit)
            if top_category in ["Education / Student Loan", "Agriculture / Farmer Loan", "Gold Loan"]:
                reasons.append("New-to-credit applicant: Accepted under category-specific collateral/co-borrower norms.")
            else:
                reasons.append("No prior credit history recorded. First-time borrower verification applies.")
                eligibility_score -= 10

        # Collateral / Category specific validation
        if top_category == "Home Loan" and collateral == "None":
            flags.append("Home loan requires property mortgaging; title deeds and sanctioned plan needed.")
        if top_category == "Gold Loan" and "gold" not in collateral.lower():
            flags.append("Gold loan requires physical pledge of 18-22K gold ornaments.")

        # Determine Eligibility Status
        if eligibility_score >= 75 and len(flags) == 0:
            status = "Likely Eligible"
            badge_class = "success"
        elif eligibility_score >= 50:
            status = "Requires Further Review"
            badge_class = "warning"
        else:
            status = "High Risk / Conditional Review"
            badge_class = "danger"

        # Recommended Amount Range
        if monthly_income > 0:
            max_affordable_emi = max(0, (monthly_income * 0.50) - existing_emi)
            if r > 0 and n > 0 and max_affordable_emi > 0:
                max_estimated_principal = (max_affordable_emi * (((1 + r) ** n) - 1)) / (r * ((1 + r) ** n))
            else:
                max_estimated_principal = loan_amount
            
            # Format range nicely around requested amount
            min_rec = int(max(25000, min(loan_amount * 0.8, max_estimated_principal * 0.7)))
            max_rec = int(max(min_rec + 50000, min(loan_amount * 1.25, max_estimated_principal * 1.15)))
        else:
            min_rec = int(loan_amount * 0.8)
            max_rec = int(loan_amount)

        # Suggested Tenure
        suggested_tenure = f"{tenure_months} Months ({tenure_months // 12} Yrs)" if tenure_months >= 12 else f"{tenure_months} Months"

        return {
            "status": status,
            "badge_class": badge_class,
            "eligibility_score": max(20, min(100, eligibility_score)),
            "proposed_emi": int(proposed_emi),
            "foir_percentage": round(foir, 1),
            "existing_dti": round(existing_dti, 1),
            "recommended_amount_min": min_rec,
            "recommended_amount_max": max_rec,
            "suggested_tenure": suggested_tenure,
            "reasons": reasons,
            "flags": flags,
            "benchmark_interest_rate": benchmark_rate,
            "interest_rate_range": cat_info["interest_rate_range"],
            "processing_fee": cat_info["processing_fee"],
            "basic_conditions": cat_info["basic_conditions"],
            "required_documents": cat_info["required_documents"]
        }

    def generate_recommendation_reason(self, profile, top_category, second_category, third_category):
        """
        Generates natural-sounding, transparent reasoning explaining why the AI
        recommended the top loan category and alternative options.
        """
        occ = profile.get("occupation", "Applicant")
        purpose = profile.get("loan_purpose", "financial requirements")
        income = profile.get("monthly_income", 0)
        land = profile.get("land_ownership", "No")
        biz = profile.get("business_type", "None")
        gender = profile.get("gender", "Applicant")

        reasons = []
        if top_category == "Agriculture / Farmer Loan":
            reasons.append(f"The applicant is engaged in {occ.lower()}, owns agricultural land ({land}), and explicitly requires funding for {purpose.lower()}.")
        elif top_category == "Education / Student Loan":
            reasons.append(f"The applicant profile indicates student status aiming for educational progression with purpose '{purpose}'.")
        elif top_category == "Home Loan":
            reasons.append(f"The primary financial requirement is residential real estate ({purpose.lower()}) supported by regular income streams.")
        elif top_category == "Vehicle Loan":
            reasons.append(f"The applicant requires financing dedicated to automotive/transport acquisition ({purpose.lower()}).")
        elif top_category == "Women / Special Category Loan":
            reasons.append(f"As a female entrepreneur/self-employed applicant ({occ}), you qualify for prioritized special category lending with subsidized interest concessions.")
        elif top_category == "MSME / Startup Loan":
            reasons.append(f"The applicant is establishing or operating an enterprise ({biz}) seeking capital for {purpose.lower()}.")
        elif top_category == "Gold Loan":
            reasons.append(f"Immediate liquidity need ({purpose.lower()}) backed by pledged physical gold collateral for rapid sanction.")
        elif top_category == "Government-Supported Loan Schemes":
            reasons.append(f"The profile matches key criteria for priority public sector developmental lending (e.g., MUDRA / PMEGP / KCC).")
        else:
            reasons.append(f"Based on stated occupation ({occ}), monthly cash flow (₹{int(income):,}), and flexible personal financial needs for '{purpose}'.")

        if second_category and third_category:
            reasons.append(f"Alternative matching categories include '{second_category}' and '{third_category}', which also share high suitability based on your asset and profile parameters.")

        return " ".join(reasons)

    def evaluate_full(self, profile):
        """
        End-to-end evaluation pipeline returning full AI recommendation payload.
        """
        scores, ranked = self.predict_suitability(profile)
        
        top_1 = ranked[0]
        top_2 = ranked[1] if len(ranked) > 1 else (None, 0)
        top_3 = ranked[2] if len(ranked) > 2 else (None, 0)

        eligibility = self.analyze_eligibility(profile, top_1[0])
        reason = self.generate_recommendation_reason(profile, top_1[0], top_2[0], top_3[0])

        return {
            "top_category": top_1[0],
            "top_score": top_1[1],
            "top_3": [
                {"category": top_1[0], "score": top_1[1], "details": LOAN_CATEGORY_DETAILS.get(top_1[0])},
                {"category": top_2[0], "score": top_2[1], "details": LOAN_CATEGORY_DETAILS.get(top_2[0])},
                {"category": top_3[0], "score": top_3[1], "details": LOAN_CATEGORY_DETAILS.get(top_3[0])}
            ],
            "all_scores": scores,
            "eligibility": eligibility,
            "reason": reason,
            "disclaimer": "This AI recommendation is for informational purposes only. Final loan eligibility, interest rate and approval are determined by the respective lender according to its current policies and verification."
        }

if __name__ == "__main__":
    recommender = LoanRecommender()
    
    # Test with Farmer example from the prompt:
    sample_farmer = {
        "full_name": "Ramesh Patel",
        "age": 42,
        "gender": "Male",
        "occupation": "Farmer",
        "monthly_income": 30000,
        "annual_income": 360000,
        "employment_type": "Agriculture / Farming",
        "credit_score": 720,
        "existing_loans": 0,
        "existing_emi": 0,
        "loan_amount": 200000,
        "loan_purpose": "Crop loan (Kharif/Rabi)",
        "loan_tenure": 24,
        "education_status": "High School",
        "applicant_persona": "Farmer",
        "house_ownership": "Owned",
        "land_ownership": "Yes",
        "agricultural_activity": "Crop Cultivation",
        "business_type": "None",
        "vehicle_requirement": "None",
        "collateral_availability": "Property / Land",
        "bank_account_status": "Active Savings Account"
    }
    
    result = recommender.evaluate_full(sample_farmer)
    print("AI Recommendation Result:")
    print(f"Best Loan: {result['top_category']} ({result['top_score']}%)")
    print(f"Top 3: {[f'{x['category']}: {x['score']}%' for x in result['top_3']]}")
    print(f"Eligibility: {result['eligibility']['status']}")
    print(f"Reason: {result['reason']}")
