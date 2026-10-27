"""
Database seeder for AI-Based Loan Detection and Recommendation System.
Seeds default Admin, Demo User, and authoritative real-benchmark Loan Schemes
across all 10 loan categories.
"""

from models import db, User, LoanScheme

DEFAULT_SCHEMES = [
    # 1. Home Loan
    {
        "category": "Home Loan",
        "bank_name": "State Bank of India (SBI)",
        "scheme_name": "SBI Regular Home Loan",
        "interest_rate_min": 8.35,
        "interest_rate_max": 9.45,
        "max_amount": 100000000.0,
        "max_tenure_months": 360,
        "processing_fee": "0.35% (Min ₹2,000, Max ₹10,000) + GST",
        "eligibility_summary": "Salaried / Self-Employed, Age 18-70, Net monthly income ₹25,000+, CIBIL 700+",
        "required_docs_summary": "Aadhaar, PAN, Last 3 months payslips, 6 months bank statement, Title deeds"
    },
    {
        "category": "Home Loan",
        "bank_name": "HDFC Bank",
        "scheme_name": "HDFC Reach Home Loan",
        "interest_rate_min": 8.50,
        "interest_rate_max": 9.75,
        "max_amount": 50000000.0,
        "max_tenure_months": 360,
        "processing_fee": "0.50% of loan amount + GST",
        "eligibility_summary": "Micro-entrepreneurs and salaried individuals without formal ITR, Min monthly income ₹15,000",
        "required_docs_summary": "KYC, Bank statement 6 months, Property agreement, Business proof or salary certificate"
    },

    # 2. Education Loan
    {
        "category": "Education / Student Loan",
        "bank_name": "State Bank of India (SBI)",
        "scheme_name": "SBI Student Loan Scheme",
        "interest_rate_min": 8.50,
        "interest_rate_max": 10.15,
        "max_amount": 15000000.0,
        "max_tenure_months": 180,
        "processing_fee": "Nil for loans up to ₹7.5 Lakhs",
        "eligibility_summary": "Indian citizen with confirmed seat in recognized degree/diploma course; Co-borrower parent required",
        "required_docs_summary": "Aadhaar, PAN of student & parents, Admission letter, Fee schedule, Academic transcripts"
    },
    {
        "category": "Education / Student Loan",
        "bank_name": "HDFC Credila",
        "scheme_name": "HDFC Credila Global Education Loan",
        "interest_rate_min": 9.25,
        "interest_rate_max": 11.85,
        "max_amount": 25000000.0,
        "max_tenure_months": 180,
        "processing_fee": "1.00% - 1.25% of loan amount",
        "eligibility_summary": "Higher education in India or abroad (US, UK, Germany, Canada, Australia); Co-borrower required",
        "required_docs_summary": "Admission letter, GRE/IELTS/TOEFL score, Co-applicant ITR, Bank statement 6 months"
    },

    # 3. Agriculture / Farmer Loan
    {
        "category": "Agriculture / Farmer Loan",
        "bank_name": "State Bank of India / NABARD",
        "scheme_name": "Kisan Credit Card (KCC) Scheme",
        "interest_rate_min": 4.00,
        "interest_rate_max": 7.00,
        "max_amount": 3000000.0,
        "max_tenure_months": 60,
        "processing_fee": "Nil for limits up to ₹3,00,000",
        "eligibility_summary": "All farmers, owner cultivators, tenant farmers, SHGs/JLGs engaged in agriculture",
        "required_docs_summary": "Aadhaar, Land ownership document (7/12 extract / Patta), Crop certificate, Bank passbook"
    },
    {
        "category": "Agriculture / Farmer Loan",
        "bank_name": "Bank of Baroda",
        "scheme_name": "Baroda Kisan Farm Mechanization Loan",
        "interest_rate_min": 7.85,
        "interest_rate_max": 9.90,
        "max_amount": 2500000.0,
        "max_tenure_months": 84,
        "processing_fee": "0.50% of loan limit",
        "eligibility_summary": "Farmers owning minimum 2 acres irrigated land for tractor and equipment purchase",
        "required_docs_summary": "Land revenue records, Dealer quotation for tractor/equipment, Aadhaar, Bank statement"
    },

    # 4. Personal Loan
    {
        "category": "Personal Loan",
        "bank_name": "State Bank of India (SBI)",
        "scheme_name": "SBI Xpress Credit Personal Loan",
        "interest_rate_min": 10.45,
        "interest_rate_max": 12.95,
        "max_amount": 3000000.0,
        "max_tenure_months": 72,
        "processing_fee": "0.50% to 1.00% + GST",
        "eligibility_summary": "Salaried employees with salary account in SBI, Net monthly income ₹20,000+, CIBIL 680+",
        "required_docs_summary": "Aadhaar, PAN, Last 3 months salary slips, 6 months bank statement"
    },
    {
        "category": "Personal Loan",
        "bank_name": "ICICI Bank",
        "scheme_name": "ICICI Instant Pre-Approved Personal Loan",
        "interest_rate_min": 10.75,
        "interest_rate_max": 14.50,
        "max_amount": 5000000.0,
        "max_tenure_months": 60,
        "processing_fee": "1.25% - 2.00% + GST",
        "eligibility_summary": "Salaried & self-employed professionals, Minimum net income ₹30,000/month",
        "required_docs_summary": "Identity proof, Address proof, 3 months salary slips, 6 months bank statement"
    },

    # 5. Business Loan
    {
        "category": "Business Loan",
        "bank_name": "Bank of Baroda",
        "scheme_name": "Baroda Business Growth Loan",
        "interest_rate_min": 10.50,
        "interest_rate_max": 14.25,
        "max_amount": 20000000.0,
        "max_tenure_months": 84,
        "processing_fee": "1.00% + GST",
        "eligibility_summary": "Existing business entities with at least 2 years continuous profitable operations",
        "required_docs_summary": "ITR & Financials (2 years), GST Returns (12 months), Bank statements, Udyam registration"
    },
    {
        "category": "Business Loan",
        "bank_name": "Tata Capital",
        "scheme_name": "Tata Working Capital & Business Loan",
        "interest_rate_min": 11.25,
        "interest_rate_max": 16.00,
        "max_amount": 7500000.0,
        "max_tenure_months": 48,
        "processing_fee": "1.50% - 2.50%",
        "eligibility_summary": "Small business enterprises, traders, retailers with annual turnover ₹20 Lakhs+",
        "required_docs_summary": "GST 3B returns, 12 months current bank statement, Business registration proof"
    },

    # 6. Vehicle Loan
    {
        "category": "Vehicle Loan",
        "bank_name": "State Bank of India (SBI)",
        "scheme_name": "SBI Car Loan Scheme",
        "interest_rate_min": 8.75,
        "interest_rate_max": 9.80,
        "max_amount": 10000000.0,
        "max_tenure_months": 84,
        "processing_fee": "Nil to 0.40%",
        "eligibility_summary": "Salaried individuals with annual income ₹3,00,000+ or Self-employed with ITR ₹4,00,000+",
        "required_docs_summary": "Aadhaar, PAN, Form 16 / ITR, 6 months bank statement, Dealer proforma invoice"
    },
    {
        "category": "Vehicle Loan",
        "bank_name": "HDFC Bank",
        "scheme_name": "HDFC Two-Wheeler Easy Loan",
        "interest_rate_min": 10.50,
        "interest_rate_max": 15.00,
        "max_amount": 350000.0,
        "max_tenure_months": 48,
        "processing_fee": "1.50% - 2.50%",
        "eligibility_summary": "Salaried or self-employed, Age 21-65, Minimum income ₹15,000/month",
        "required_docs_summary": "KYC documents, Bank statement 3 months, Vehicle dealer price quotation"
    },

    # 7. Gold Loan
    {
        "category": "Gold Loan",
        "bank_name": "Muthoot Finance",
        "scheme_name": "Muthoot Instant Express Gold Loan",
        "interest_rate_min": 7.50,
        "interest_rate_max": 11.90,
        "max_amount": 10000000.0,
        "max_tenure_months": 24,
        "processing_fee": "0.25% - 0.50% (Max ₹1,500)",
        "eligibility_summary": "Any individual possessing genuine gold ornaments of 18-22 carat purity",
        "required_docs_summary": "Aadhaar Card, PAN Card, Passport size photo, Gold ornaments for assay"
    },
    {
        "category": "Gold Loan",
        "bank_name": "State Bank of India (SBI)",
        "scheme_name": "SBI Personal Gold Loan",
        "interest_rate_min": 8.25,
        "interest_rate_max": 9.50,
        "max_amount": 5000000.0,
        "max_tenure_months": 36,
        "processing_fee": "0.25% + GST (Min ₹250)",
        "eligibility_summary": "Individuals with steady source of income, Age 18+",
        "required_docs_summary": "Aadhaar / Voter ID, Two photographs, Witness verification for gold pledge"
    },

    # 8. MSME / Startup Loan
    {
        "category": "MSME / Startup Loan",
        "bank_name": "SIDBI / CGTMSE",
        "scheme_name": "CGTMSE Collateral-Free Credit Scheme",
        "interest_rate_min": 8.50,
        "interest_rate_max": 11.50,
        "max_amount": 50000000.0,
        "max_tenure_months": 84,
        "processing_fee": "0.50% - 1.00%",
        "eligibility_summary": "New and existing micro and small enterprises (Manufacturing & Services), Udyam registered",
        "required_docs_summary": "Udyam Certificate, Detailed Project Report (DPR), Projected balance sheet, KYC"
    },
    {
        "category": "MSME / Startup Loan",
        "bank_name": "Punjab National Bank",
        "scheme_name": "PNB Sanjeevani MSME Scheme",
        "interest_rate_min": 8.90,
        "interest_rate_max": 12.00,
        "max_amount": 20000000.0,
        "max_tenure_months": 84,
        "processing_fee": "0.75%",
        "eligibility_summary": "MSME units with viable business model, GST registration, Minimum promoter equity 20%",
        "required_docs_summary": "Promoter KYC, GST returns, Audited balance sheet, Industrial license/NOC"
    },

    # 9. Women / Special Category Loan
    {
        "category": "Women / Special Category Loan",
        "bank_name": "Government of India / Stand-Up India",
        "scheme_name": "Stand-Up India Scheme for Women Entrepreneurs",
        "interest_rate_min": 7.50,
        "interest_rate_max": 9.75,
        "max_amount": 10000000.0,
        "max_tenure_months": 84,
        "processing_fee": "Concessional / Zero fee",
        "eligibility_summary": "Women entrepreneurs (at least 51% shareholding) setting up greenfield manufacturing, service or trading unit",
        "required_docs_summary": "Aadhaar, PAN, Proof of 51% female ownership, Detailed project proposal, Bank statement"
    },
    {
        "category": "Women / Special Category Loan",
        "bank_name": "State Bank of India (SBI)",
        "scheme_name": "SBI Stree Shakti Package",
        "interest_rate_min": 7.80,
        "interest_rate_max": 10.20,
        "max_amount": 5000000.0,
        "max_tenure_months": 60,
        "processing_fee": "Waived / Discounted",
        "eligibility_summary": "Women-led micro businesses enrolled in state entrepreneurship EDP programs",
        "required_docs_summary": "Identity proof, Business registration, EDP completion certificate, Bank statements"
    },

    # 10. Government-Supported Loan Schemes
    {
        "category": "Government-Supported Loan Schemes",
        "bank_name": "Ministry of Finance / All Scheduled Banks",
        "scheme_name": "Pradhan Mantri MUDRA Yojana (PMMY)",
        "interest_rate_min": 7.30,
        "interest_rate_max": 10.00,
        "max_amount": 1000000.0,
        "max_tenure_months": 60,
        "processing_fee": "Nil for Shishu (up to ₹50k) and Kishore (up to ₹5L)",
        "eligibility_summary": "Non-corporate, non-farm small/micro enterprises for income generation",
        "required_docs_summary": "MUDRA application form, Aadhaar, Proof of identity and business address, Machinery quotation"
    },
    {
        "category": "Government-Supported Loan Schemes",
        "bank_name": "KVIC / Ministry of MSME",
        "scheme_name": "PMEGP (Prime Minister Employment Generation Programme)",
        "interest_rate_min": 6.75,
        "interest_rate_max": 9.50,
        "max_amount": 5000000.0,
        "max_tenure_months": 84,
        "processing_fee": "Nil",
        "eligibility_summary": "Individuals above 18 years for new self-employment ventures; 15% to 35% Govt capital subsidy",
        "required_docs_summary": "PMEGP Online form, Aadhaar, Educational certificate (8th pass for >10L project), Project report"
    }
]

def seed_database(app):
    with app.app_context():
        db.create_all()

        # Seed Admin user if not exists
        admin = User.query.filter_by(email="admin@loanai.com").first()
        if not admin:
            admin = User(
                name="System Administrator",
                email="admin@loanai.com",
                phone="+91 9876543210",
                role="admin"
            )
            admin.set_password("Admin@1234")
            db.session.add(admin)
            print("[Seeder] Created Admin user: admin@loanai.com / Admin@1234")

        # Seed Demo User if not exists
        demo_user = User.query.filter_by(email="ramesh.patel@example.com").first()
        if not demo_user:
            demo_user = User(
                name="Ramesh Patel",
                email="ramesh.patel@example.com",
                phone="+91 9820011223",
                role="user"
            )
            demo_user.set_password("User@1234")
            db.session.add(demo_user)
            print("[Seeder] Created Demo user: ramesh.patel@example.com / User@1234")

        # Seed Loan Schemes if empty
        if LoanScheme.query.count() == 0:
            for s in DEFAULT_SCHEMES:
                scheme = LoanScheme(
                    category=s["category"],
                    bank_name=s["bank_name"],
                    scheme_name=s["scheme_name"],
                    interest_rate_min=s["interest_rate_min"],
                    interest_rate_max=s["interest_rate_max"],
                    max_amount=s["max_amount"],
                    max_tenure_months=s["max_tenure_months"],
                    processing_fee=s["processing_fee"],
                    eligibility_summary=s["eligibility_summary"],
                    required_docs_summary=s["required_docs_summary"],
                    is_active=True
                )
                db.session.add(scheme)
            db.session.commit()
            print(f"[Seeder] Seeded {len(DEFAULT_SCHEMES)} benchmark loan schemes across 10 categories.")
        else:
            db.session.commit()
            print(f"[Seeder] Database already contains {LoanScheme.query.count()} loan schemes.")
