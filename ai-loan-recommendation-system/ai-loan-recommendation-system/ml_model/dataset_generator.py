"""
Dataset generator for AI-Based Loan Detection and Recommendation System.
Generates a realistic, diverse dataset of 8,000+ loan applicant profiles
across 10 target loan categories with nuanced financial, demographic,
and asset characteristics.
"""

import numpy as np
import pandas as pd
import random

LOAN_CATEGORIES = [
    "Home Loan",
    "Education / Student Loan",
    "Agriculture / Farmer Loan",
    "Personal Loan",
    "Business Loan",
    "Vehicle Loan",
    "Gold Loan",
    "MSME / Startup Loan",
    "Women / Special Category Loan",
    "Government-Supported Loan Schemes"
]

PURPOSE_MAPPING = {
    "Home Loan": [
        "Buying a new house", "Constructing a house", "Buying a flat / apartment",
        "Home renovation / extension", "Plot purchase & construction"
    ],
    "Education / Student Loan": [
        "College education fees", "Higher studies / Master's degree",
        "Professional courses (Medical/Engg/MBA)", "Study abroad expenses", "Vocational skill training"
    ],
    "Agriculture / Farmer Loan": [
        "Crop loan (Kharif/Rabi)", "Farming equipment purchase", "Tractor loan for farm",
        "Irrigation / Borewell installation", "Seeds, fertilizers & pesticides",
        "Dairy farming setup", "Poultry farming setup", "Agricultural land development"
    ],
    "Personal Loan": [
        "Medical emergency expenses", "Marriage / Wedding expenses",
        "Urgent family emergency", "Travel / Vacation financing",
        "Personal debt consolidation", "Household appliance / consumer durable"
    ],
    "Business Loan": [
        "Starting a new commercial business", "Business expansion / New branch",
        "Working capital for inventory", "Commercial machinery purchase", "Small enterprise vendor payments"
    ],
    "Vehicle Loan": [
        "Two-wheeler / Motorcycle purchase", "Personal Car (Hatchback/Sedan/SUV)",
        "Commercial vehicle (Tempo/Truck/Taxi)", "Farm / Commercial Tractor"
    ],
    "Gold Loan": [
        "Short-term emergency cash against gold", "Urgent liquidity need (Pledging gold)",
        "Instant agricultural/medical emergency against gold ornaments"
    ],
    "MSME / Startup Loan": [
        "Tech / Innovation Startup launch", "Small manufacturing unit setup",
        "Service enterprise launch", "Greenfield MSME project", "Scale-up capital for registered MSME"
    ],
    "Women / Special Category Loan": [
        "Women entrepreneur venture", "Self-help group / Self-employment for women",
        "Boutique / Handicraft / Home-based enterprise", "Women micro-enterprise expansion"
    ],
    "Government-Supported Loan Schemes": [
        "PM MUDRA Yojana (Shishu/Kishore/Tarun)", "PMEGP (Prime Minister Employment Gen)",
        "Stand-Up India Scheme", "Kisan Credit Card (KCC) subsidized",
        "Credit Guarantee Fund Scheme for Micro Enterprises", "Central Sector Interest Subsidy Education"
    ]
}

def generate_applicant(category_hint=None):
    category = category_hint or random.choice(LOAN_CATEGORIES)
    purpose = random.choice(PURPOSE_MAPPING[category])
    
    # Defaults
    gender = random.choices(["Male", "Female", "Other"], weights=[0.55, 0.42, 0.03])[0]
    
    if category == "Women / Special Category Loan":
        gender = "Female"
        age = random.randint(21, 58)
        occupation = random.choices(["Homemaker / Self-employed Woman", "Business Owner", "Self-Employed Professional"], weights=[0.5, 0.3, 0.2])[0]
        applicant_persona = random.choices(["Business", "Working"], weights=[0.7, 0.3])[0]
        employment_type = random.choices(["Self-Employed", "Business Enterprise"], weights=[0.6, 0.4])[0]
        monthly_income = random.randint(15000, 120000)
        credit_score = random.randint(580, 820)
        loan_amount = random.randint(50000, 1500000)
        loan_tenure = random.choice([12, 24, 36, 48, 60])
        collateral = random.choices(["None", "Property / Land", "Gold / Ornaments"], weights=[0.6, 0.2, 0.2])[0]
        land_ownership = random.choice(["No", "Yes"])
        agricultural_activity = "None"
        business_type = random.choice(["Home-based Enterprise", "Retail Shop", "Services"])
        vehicle_requirement = "None"
        house_ownership = random.choice(["Owned", "Rented", "Ancestral"])
        education_status = random.choice(["Graduate", "High School", "Vocational / Diploma", "Undergraduate"])
        
    elif category == "Education / Student Loan":
        age = random.randint(17, 28)
        occupation = "Student"
        applicant_persona = "Student"
        employment_type = "Student / Unemployed"
        monthly_income = random.randint(0, 25000)
        credit_score = random.choice([0, random.randint(550, 780)])
        loan_amount = random.randint(80000, 3500000)
        loan_tenure = random.choice([36, 48, 60, 84, 120])
        collateral = random.choices(["None", "Property / Land", "Fixed Deposit / Securities"], weights=[0.65, 0.25, 0.1])[0]
        land_ownership = "No"
        agricultural_activity = "None"
        business_type = "None"
        vehicle_requirement = "None"
        house_ownership = random.choice(["Owned", "Rented", "Ancestral"])
        education_status = random.choice(["Undergraduate", "Graduate", "High School"])
        
    elif category == "Agriculture / Farmer Loan":
        age = random.randint(22, 65)
        occupation = "Farmer"
        applicant_persona = "Farmer"
        employment_type = "Agriculture / Farming"
        monthly_income = random.randint(12000, 100000)
        credit_score = random.randint(550, 800)
        loan_amount = random.randint(40000, 1200000)
        loan_tenure = random.choice([12, 24, 36, 48, 60, 84])
        land_ownership = "Yes"
        collateral = random.choices(["Property / Land", "None", "Machinery / Stock"], weights=[0.7, 0.2, 0.1])[0]
        agricultural_activity = random.choice(["Crop Cultivation", "Dairy Farming", "Poultry Farming", "Horticulture", "Agro-processing"])
        business_type = "None"
        if "Tractor" in purpose:
            vehicle_requirement = "Tractor"
        else:
            vehicle_requirement = random.choices(["None", "Two-Wheeler", "Tractor"], weights=[0.7, 0.2, 0.1])[0]
        house_ownership = random.choice(["Owned", "Ancestral"])
        education_status = random.choice(["Primary / None", "High School", "Vocational / Diploma", "Graduate"])
        
    elif category == "Home Loan":
        age = random.randint(24, 58)
        occupation = random.choices(["Salaried", "Self-Employed Professional", "Business Owner"], weights=[0.7, 0.2, 0.1])[0]
        applicant_persona = "Working"
        employment_type = random.choices(["Full-Time Salaried", "Government Service", "Self-Employed"], weights=[0.65, 0.25, 0.1])[0]
        monthly_income = random.randint(35000, 350000)
        credit_score = random.randint(620, 850)
        loan_amount = random.randint(800000, 10000000)
        loan_tenure = random.choice([60, 120, 180, 240, 300])
        collateral = "Property / Land"
        land_ownership = random.choice(["Yes", "No"])
        agricultural_activity = "None"
        business_type = "None"
        vehicle_requirement = "None"
        house_ownership = random.choice(["Rented", "Ancestral", "Owned"])
        education_status = random.choice(["Graduate", "Postgraduate", "Vocational / Diploma"])
        
    elif category == "Business Loan":
        age = random.randint(25, 62)
        occupation = random.choices(["Business Owner", "Self-Employed Professional"], weights=[0.8, 0.2])[0]
        applicant_persona = "Business"
        employment_type = "Business Enterprise"
        monthly_income = random.randint(40000, 450000)
        credit_score = random.randint(600, 830)
        loan_amount = random.randint(200000, 6000000)
        loan_tenure = random.choice([12, 24, 36, 48, 60])
        collateral = random.choices(["Property / Land", "Machinery / Stock", "None"], weights=[0.4, 0.3, 0.3])[0]
        land_ownership = random.choice(["Yes", "No"])
        agricultural_activity = "None"
        business_type = random.choice(["Retail Shop", "Manufacturing", "Services", "Wholesale / Trading"])
        vehicle_requirement = random.choices(["None", "Commercial Vehicle"], weights=[0.8, 0.2])[0]
        house_ownership = random.choice(["Owned", "Rented", "Ancestral"])
        education_status = random.choice(["Graduate", "Postgraduate", "High School", "Vocational / Diploma"])
        
    elif category == "MSME / Startup Loan":
        age = random.randint(21, 50)
        occupation = random.choices(["Business Owner", "Self-Employed Professional"], weights=[0.7, 0.3])[0]
        applicant_persona = "Business"
        employment_type = "Business Enterprise"
        monthly_income = random.randint(25000, 250000)
        credit_score = random.randint(620, 820)
        loan_amount = random.randint(150000, 5000000)
        loan_tenure = random.choice([12, 24, 36, 60, 84])
        collateral = random.choices(["None", "Property / Land", "Machinery / Stock"], weights=[0.5, 0.3, 0.2])[0]
        land_ownership = random.choice(["No", "Yes"])
        agricultural_activity = "None"
        business_type = random.choice(["Tech Startup", "Manufacturing", "Services", "Retail Shop"])
        vehicle_requirement = "None"
        house_ownership = random.choice(["Owned", "Rented"])
        education_status = random.choice(["Graduate", "Postgraduate"])
        
    elif category == "Vehicle Loan":
        age = random.randint(21, 60)
        occupation = random.choices(["Salaried", "Self-Employed Professional", "Business Owner", "Gig Worker / Driver"], weights=[0.5, 0.2, 0.2, 0.1])[0]
        applicant_persona = "Working"
        employment_type = random.choices(["Full-Time Salaried", "Self-Employed", "Contractual Salaried"], weights=[0.6, 0.3, 0.1])[0]
        monthly_income = random.randint(20000, 200000)
        credit_score = random.randint(600, 820)
        
        if "Two-wheeler" in purpose:
            loan_amount = random.randint(40000, 180000)
            loan_tenure = random.choice([12, 24, 36])
            vehicle_requirement = "Two-Wheeler"
        elif "Car" in purpose:
            loan_amount = random.randint(300000, 2000000)
            loan_tenure = random.choice([24, 36, 48, 60, 84])
            vehicle_requirement = "Four-Wheeler / Car"
        elif "Commercial" in purpose:
            loan_amount = random.randint(400000, 3000000)
            loan_tenure = random.choice([24, 36, 48, 60])
            vehicle_requirement = "Commercial Vehicle"
        else:
            loan_amount = random.randint(300000, 1200000)
            loan_tenure = random.choice([24, 36, 48, 60])
            vehicle_requirement = "Tractor"
            
        collateral = "Machinery / Stock"  # Vehicle acts as hypothecation
        land_ownership = random.choice(["No", "Yes"])
        agricultural_activity = "None"
        business_type = "None"
        house_ownership = random.choice(["Owned", "Rented", "Ancestral"])
        education_status = random.choice(["Graduate", "High School", "Vocational / Diploma"])
        
    elif category == "Gold Loan":
        age = random.randint(20, 65)
        occupation = random.choices(["Salaried", "Business Owner", "Farmer", "Daily Wage Worker / Artisan", "Homemaker / Self-employed Woman"], weights=[0.3, 0.2, 0.2, 0.15, 0.15])[0]
        applicant_persona = random.choice(["Working", "Business", "Farmer"])
        employment_type = random.choice(["Full-Time Salaried", "Self-Employed", "Agriculture / Farming", "Contractual Salaried"])
        monthly_income = random.randint(15000, 150000)
        credit_score = random.randint(450, 780)
        loan_amount = random.randint(30000, 1500000)
        loan_tenure = random.choice([6, 12, 18, 24])
        collateral = "Gold / Ornaments"
        land_ownership = random.choice(["No", "Yes"])
        agricultural_activity = "None"
        business_type = "None"
        vehicle_requirement = "None"
        house_ownership = random.choice(["Owned", "Rented", "Ancestral"])
        education_status = random.choice(["High School", "Graduate", "Primary / None"])
        
    elif category == "Government-Supported Loan Schemes":
        age = random.randint(18, 60)
        occupation = random.choices(["Farmer", "Homemaker / Self-employed Woman", "Daily Wage Worker / Artisan", "Student", "Business Owner"], weights=[0.3, 0.25, 0.2, 0.15, 0.1])[0]
        applicant_persona = random.choice(["Farmer", "Business", "Student", "Working"])
        employment_type = random.choice(["Agriculture / Farming", "Self-Employed", "Student / Unemployed", "Contractual Salaried"])
        monthly_income = random.randint(10000, 70000)
        credit_score = random.randint(520, 760)
        loan_amount = random.randint(50000, 1000000)
        loan_tenure = random.choice([24, 36, 60, 84])
        collateral = random.choices(["None", "Property / Land"], weights=[0.8, 0.2])[0]
        land_ownership = "Yes" if occupation == "Farmer" else random.choice(["No", "Yes"])
        agricultural_activity = "Crop Cultivation" if occupation == "Farmer" else "None"
        business_type = "Home-based Enterprise" if "MUDRA" in purpose or "PMEGP" in purpose else "None"
        vehicle_requirement = "None"
        house_ownership = random.choice(["Ancestral", "Rented", "Owned"])
        education_status = random.choice(["High School", "Vocational / Diploma", "Graduate", "Primary / None"])
        
    else:  # Personal Loan
        age = random.randint(21, 58)
        occupation = random.choices(["Salaried", "Self-Employed Professional", "Gig Worker / Driver"], weights=[0.75, 0.2, 0.05])[0]
        applicant_persona = "Working"
        employment_type = random.choices(["Full-Time Salaried", "Government Service", "Contractual Salaried"], weights=[0.6, 0.3, 0.1])[0]
        monthly_income = random.randint(22000, 220000)
        credit_score = random.randint(580, 820)
        loan_amount = random.randint(30000, 1500000)
        loan_tenure = random.choice([12, 24, 36, 48, 60])
        collateral = "None"
        land_ownership = random.choice(["No", "Yes"])
        agricultural_activity = "None"
        business_type = "None"
        vehicle_requirement = "None"
        house_ownership = random.choice(["Rented", "Owned", "Ancestral"])
        education_status = random.choice(["Graduate", "Postgraduate", "High School"])

    annual_income = monthly_income * 12
    existing_loans = random.choices([0, 1, 2, 3], weights=[0.45, 0.35, 0.15, 0.05])[0]
    existing_emi = 0
    if existing_loans > 0:
        max_possible_emi = int(monthly_income * 0.45)
        existing_emi = random.randint(2000, max(2500, max_possible_emi))
        
    bank_account_status = random.choices(
        ["Salary Account", "Active Savings Account", "Current Account", "Jan Dhan Account"],
        weights=[0.4, 0.35, 0.15, 0.1]
    )[0]
    
    return {
        "age": age,
        "gender": gender,
        "occupation": occupation,
        "monthly_income": monthly_income,
        "annual_income": annual_income,
        "employment_type": employment_type,
        "credit_score": credit_score,
        "existing_loans": existing_loans,
        "existing_emi": existing_emi,
        "loan_amount": loan_amount,
        "loan_purpose": purpose,
        "loan_tenure": loan_tenure,
        "education_status": education_status,
        "applicant_persona": applicant_persona,
        "house_ownership": house_ownership,
        "land_ownership": land_ownership,
        "agricultural_activity": agricultural_activity,
        "business_type": business_type,
        "vehicle_requirement": vehicle_requirement,
        "collateral_availability": collateral,
        "bank_account_status": bank_account_status,
        "loan_category": category
    }

def generate_dataset(num_samples=8000):
    data = []
    # Balance across categories
    samples_per_cat = num_samples // len(LOAN_CATEGORIES)
    for cat in LOAN_CATEGORIES:
        for _ in range(samples_per_cat):
            data.append(generate_applicant(cat))
    
    # Extra random variations
    remainder = num_samples - len(data)
    for _ in range(remainder):
        data.append(generate_applicant())
        
    df = pd.DataFrame(data)
    # Shuffle
    df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
    return df

if __name__ == "__main__":
    df = generate_dataset(8000)
    print(f"Generated dataset with {len(df)} records.")
    print("Class distribution:")
    print(df["loan_category"].value_counts())
    df.to_csv("loan_applicants_dataset.csv", index=False)
    print("Saved to loan_applicants_dataset.csv")
