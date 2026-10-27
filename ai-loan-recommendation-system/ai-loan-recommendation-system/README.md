# AI-Based Loan Detection and Recommendation System (LoanAI)

An intelligent, machine-learning-driven financial recommendation and underwriting system that analyzes an applicant's personal, financial, employment, education, business, farming, and asset profiles across **10 distinct loan categories**. 

The system computes precise category suitability percentages, recommends the **Top 3 matching loan categories**, performs deep **Financial Eligibility & FOIR/DTI Debt-to-Income analysis**, provides a **real-benchmark loan scheme comparison matrix**, and features an **Online Document Submission Station with Live Device Camera Scanning**.

---

## 🌟 Key Features

1. **AI/ML Multi-Category Loan Classifier**:
   - Built with **Scikit-learn** using a `RandomForestClassifier` pipeline with categorical one-hot encoding and standard scaling.
   - Trained on 8,500+ diverse applicant profiles achieving **99.65% classification accuracy**.
   - Outputs probabilistic suitability scores across all 10 loan categories rather than a single generic prediction.
   - Identifies the primary loan purpose first and highlights the **Top 3 suitable loan categories**.

2. **10 Detected Loan Categories**:
   - 🏠 **Home Loan** (Purchase, construction, flats, renovation)
   - 🎓 **Education / Student Loan** (College fees, higher studies, professional degrees, study abroad)
   - 🌾 **Agriculture / Farmer Loan** (KCC crop loans, tractors, farm equipment, irrigation, dairy, poultry)
   - 👤 **Personal Loan** (Medical emergencies, marriage, travel, debt consolidation)
   - 💼 **Business Loan** (Starting a business, expansion, working capital, commercial machinery)
   - 🚗 **Vehicle Loan** (Two-wheelers, passenger cars, commercial vehicles, tractors)
   - 🪙 **Gold Loan** (Instant emergency liquidity pledged against physical gold ornaments)
   - 🚀 **MSME / Startup Loan** (Tech innovation startups, small manufacturing, service units)
   - 👩‍💼 **Women / Special Category Loan** (Women-led ventures, self-help groups, concessional rates)
   - 🏛️ **Government-Supported Loan Schemes** (PM MUDRA Shishu/Kishore/Tarun, PMEGP, Stand-Up India)

3. **Comprehensive 26+ Input Form**:
   - **Personal & Contact:** Full Name, Age, Gender, Mobile Number.
   - **Location:** State, District, City/Village.
   - **Employment & Financial:** Occupation, Monthly Income, Annual Income, Employment Type, Company/Business Name, Credit Score (300-900), Existing Loans Count, Existing Monthly EMI, Bank Account Status.
   - **Loan Requirement:** Loan Amount Required, Loan Purpose (with smart datalist suggestions), Loan Tenure Required, Applicant Persona (Student/Working/Business/Farmer).
   - **Profile & Assets:** Education Status, House Ownership, Land Ownership, Agricultural Activity, Business Type, Vehicle Requirement, Collateral Availability.
   - **1-Click Demo Prefill Chips:** Rapid testing presets for Farmer, Student, Salaried Home Buyer, Woman Entrepreneur, and Business Owner.

4. **Financial Eligibility Analysis & Scoring Engine**:
   - Evaluates **FOIR (Fixed Obligation to Income Ratio)** and **Debt-to-Income (DTI)** against banking thresholds.
   - Assesses **Credit Score tiers** (Excellent, Good, Fair, New to Credit).
   - Computes **Recommended Loan Amount Range** and **Suggested Tenure**.
   - Generates transparent, natural-language **AI Match Reasoning**.
   - Evaluates applicant repayment capacity and displays **Likely Eligible / Requires Further Review / High Risk** badges.
   - Mandatory banking disclaimer regarding lender final approval.

5. **Integrated Online Document Submission & Live Camera Scanner**:
   - **📷 Device Camera Scanning:** Live WebRTC video stream (`navigator.mediaDevices.getUserMedia`) for scanning Aadhaar, PAN, Land records, or income proofs.
   - **Audio & Visual Shutter:** Synthetic camera shutter click sound and flash animation upon capture.
   - **Canvas Snapshot:** Captures high-resolution images with document frame guides.
   - **Dual Camera Support:** One-click flip between environment (rear) and user (front) cameras.
   - **Retake / Replace:** Review captured image and easily retake before submission.
   - **📁 Direct File Upload:** Drag-and-drop or select JPG, PNG, or PDF files.
   - **👁️ Document Preview:** High-resolution zoomable preview modal.
   - **Real-Time Verification Tracking:** Status badges (`Pending Verification`, `Verified`, `Rejected`).

6. **Interactive Loan EMI Calculator**:
   - Dynamic sliders for Loan Amount, Loan Tenure, and Interest Rate.
   - Real-time Chart.js donut breakdown of Principal Amount vs. Total Interest.

7. **Loan Comparison Matrix**:
   - Compares matching products from leading institutions (State Bank of India, HDFC, Bank of Baroda, PMMY, Muthoot, SIDBI).
   - Instant "Apply to EMI Calculator" button for any scheme.

8. **Administrative Verification Portal**:
   - **Dashboard:** Application metrics, category distribution doughnut chart, verification backlog.
   - **Application Review:** Full 26-parameter profile audit, AI score distribution, and underwriter status updates.
   - **Document Verification Desk:** Admin can inspect high-resolution camera scans, **Approve** (`Verified`), or **Reject with Reason** (`Rejected`).
   - **Schemes Registry:** Add or edit benchmark loan products and interest rate ranges.
   - **User Accounts:** Manage registered applicant accounts.

---

## 🛠️ Technology Stack

- **Backend:** Python 3.13, Flask 3.1, Flask-Login, Flask-SQLAlchemy, Werkzeug
- **AI / Machine Learning:** Scikit-learn (RandomForestClassifier, ColumnTransformer, StandardScaler, OneHotEncoder), Pandas, NumPy, Joblib
- **Database:** SQLite (default zero-configuration) or MySQL (via `DATABASE_URL`)
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Chart.js 4.4, FontAwesome 6, WebRTC MediaDevices API, Web Audio API

---

## 📁 Project Structure

```
ai-loan-recommendation-system/
│
├── app.py                      # Main Flask application and API routes
├── models.py                   # SQLAlchemy models (User, LoanApplication, Document, Scheme)
├── seed_data.py                # Database seeder with benchmark schemes & default users
├── test_app.py                 # Automated end-to-end unit test suite
├── README.md                   # System documentation
│
├── ml_model/
│   ├── dataset_generator.py    # Synthetic 8,500-sample balanced dataset generator
│   ├── train_model.py          # Scikit-learn model training pipeline
│   ├── recommender.py          # AI recommendation & eligibility calculation engine
│   └── loan_classifier_pipeline.joblib  # Trained model artifact (99.65% accuracy)
│
├── static/
│   ├── css/
│   │   └── style.css           # Custom FinTech styles, camera viewport, badges
│   └── js/
│       ├── main.js             # Demo autofill chips & interactive EMI calculator
│       └── camera.js           # Live WebRTC camera scanner, shutter click, & preview
│
├── templates/
│   ├── base.html               # Master layout with responsive navbar & footer
│   ├── index.html              # Landing page showcasing categories & features
│   ├── login.html              # Sign in with 1-click test credentials
│   ├── register.html           # User registration
│   ├── detect_loan.html        # Comprehensive 26-field input form
│   ├── result.html             # AI Recommendation dashboard & Camera scanning station
│   ├── dashboard.html          # Applicant dashboard & application history
│   └── admin/
│       ├── dashboard.html      # Admin overview with charts & pending doc queue
│       ├── applications.html   # Applications table with filters
│       ├── view_application.html # Full profile audit & Document Verification Desk
│       ├── schemes.html        # Benchmark schemes registry & creation modal
│       └── users.html          # User account management
│
└── uploads/                    # Secure local storage for scanned/uploaded documents
```

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure Python 3.10+ is installed.

### 2. Run the Application
Open a terminal in the project directory:

```bash
cd C:\Users\Admin\.gemini\antigravity\scratch\ai-loan-recommendation-system
python app.py
```

The application will start on `http://127.0.0.1:5000/`.

---

## 🔑 Default Login Credentials

For quick testing, the login screen includes 1-click auto-fill buttons for both roles:

| Role | Email | Password | Access |
| :--- | :--- | :--- | :--- |
| **Applicant (Demo)** | `ramesh.patel@example.com` | `User@1234` | Full applicant portal, AI detection form, document upload/scan |
| **Administrator** | `admin@loanai.com` | `Admin@1234` | Underwriting portal, document verification desk, scheme manager |

---

## 🧪 Running Automated Tests

Run the automated test suite to verify database seeding, the Farmer test case, camera snapshot submissions, and admin approvals/rejections:

```bash
python test_app.py
```

**Expected output:**
```
Ran 4 tests in 1.8s
OK
[TEST 1 PASS] Seeder verified: 20 schemes and default users ready.
[TEST 2 PASS] Farmer AI Evaluation: Top Match 'Agriculture / Farmer Loan' with 96%.
[TEST 3 PASS] Camera scan uploaded successfully: scan_8f0cda78_Aadhaar_Card.jpg (Status: Pending Verification)
[TEST 4A PASS] Admin approved document: Verification status is 'Verified'
[TEST 4B PASS] Admin rejected document with reason: 'Stamp and seal blurry, please rescan in sunlight.'
```

---

## 🌐 MySQL Configuration (Optional)

By default, the application runs frictionlessly using SQLite (`loan_system.db`). If you wish to connect to a MySQL database:

1. Create a MySQL database:
   ```sql
   CREATE DATABASE loan_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
2. Set the `DATABASE_URL` environment variable before running `app.py`:
   ```powershell
   $env:DATABASE_URL="mysql+mysqlconnector://root:password@localhost/loan_system"
   python app.py
   ```
