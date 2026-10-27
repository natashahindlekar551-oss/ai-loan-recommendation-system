"""
Main Flask Application for AI-Based Loan Detection and Recommendation System.
Provides AI inference, user authentication, application tracking,
document upload & live camera scanning, and an administrative verification portal.
"""

import os
import json
import base64
import uuid
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, send_from_directory, abort
)
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)
from werkzeug.utils import secure_filename

from models import db, User, LoanApplication, ApplicationDocument, LoanScheme
from ml_model.recommender import LoanRecommender, LOAN_CATEGORY_DETAILS
from seed_data import seed_database

# Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf", "webp"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "ai-loan-secure-key-2026-x9z1")
# Support SQLite default or MySQL via DATABASE_URL
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'loan_system.db')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "info"
login_manager.init_app(app)

# Initialize AI Recommender Engine
recommender = LoanRecommender()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Seed database on startup
with app.app_context():
    seed_database(app)

# -------------------------------------------------------------
# Public & Authentication Routes
# -------------------------------------------------------------

@app.route("/")
def index():
    schemes_count = LoanScheme.query.filter_by(is_active=True).count()
    return render_template("index.html", schemes_count=schemes_count, categories=list(LOAN_CATEGORY_DETAILS.keys()))

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        phone = request.form.get("phone", "").strip()

        if not name or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("An account with this email address already exists.", "warning")
            return render_template("register.html")

        new_user = User(name=name, email=email, phone=phone, role="user")
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash("Registration successful! Welcome to AI Loan Portal.", "success")
        return redirect(url_for("detect_loan"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash(f"Welcome back, {user.name}!", "success")
            next_page = request.args.get("next")
            if next_page:
                return redirect(next_page)
            if user.is_admin:
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("index"))

# -------------------------------------------------------------
# User Dashboard & Profile
# -------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    applications = (
        LoanApplication.query.filter_by(user_id=current_user.id)
        .order_by(LoanApplication.created_at.desc())
        .all()
    )
    return render_template("dashboard.html", applications=applications)

# -------------------------------------------------------------
# AI Loan Detection Form & Prediction
# -------------------------------------------------------------

@app.route("/detect-loan", methods=["GET", "POST"])
@login_required
def detect_loan():
    if request.method == "POST":
        try:
            # Extract form data for all 26+ fields
            form_data = {
                "full_name": request.form.get("full_name", current_user.name).strip(),
                "age": int(request.form.get("age", 30)),
                "gender": request.form.get("gender", "Male"),
                "mobile": request.form.get("mobile", current_user.phone or "").strip(),
                "state": request.form.get("state", "").strip(),
                "district": request.form.get("district", "").strip(),
                "city_village": request.form.get("city_village", "").strip(),
                "occupation": request.form.get("occupation", "Salaried"),
                "monthly_income": float(request.form.get("monthly_income", 0)),
                "annual_income": float(request.form.get("annual_income", 0)) or (float(request.form.get("monthly_income", 0)) * 12),
                "employment_type": request.form.get("employment_type", "Full-Time Salaried"),
                "company_name": request.form.get("company_name", "").strip(),
                "credit_score": int(request.form.get("credit_score", 700)),
                "existing_loans": int(request.form.get("existing_loans", 0)),
                "existing_emi": float(request.form.get("existing_emi", 0)),
                "loan_amount": float(request.form.get("loan_amount", 100000)),
                "loan_purpose": request.form.get("loan_purpose", "").strip(),
                "loan_tenure": int(request.form.get("loan_tenure", 36)),
                "education_status": request.form.get("education_status", "Graduate"),
                "applicant_persona": request.form.get("applicant_persona", "Working"),
                "house_ownership": request.form.get("house_ownership", "Owned"),
                "land_ownership": request.form.get("land_ownership", "No"),
                "agricultural_activity": request.form.get("agricultural_activity", "None"),
                "business_type": request.form.get("business_type", "None"),
                "vehicle_requirement": request.form.get("vehicle_requirement", "None"),
                "collateral_availability": request.form.get("collateral_availability", "None"),
                "bank_account_status": request.form.get("bank_account_status", "Active Savings Account"),
            }

            # Run AI Recommendation & Eligibility Engine
            ai_result = recommender.evaluate_full(form_data)

            # Persist application in database
            top_3 = ai_result["top_3"]
            application = LoanApplication(
                user_id=current_user.id,
                full_name=form_data["full_name"],
                age=form_data["age"],
                gender=form_data["gender"],
                mobile=form_data["mobile"],
                state=form_data["state"],
                district=form_data["district"],
                city_village=form_data["city_village"],
                occupation=form_data["occupation"],
                monthly_income=form_data["monthly_income"],
                annual_income=form_data["annual_income"],
                employment_type=form_data["employment_type"],
                company_name=form_data["company_name"],
                credit_score=form_data["credit_score"],
                existing_loans=form_data["existing_loans"],
                existing_emi=form_data["existing_emi"],
                loan_amount=form_data["loan_amount"],
                loan_purpose=form_data["loan_purpose"],
                loan_tenure=form_data["loan_tenure"],
                education_status=form_data["education_status"],
                applicant_persona=form_data["applicant_persona"],
                house_ownership=form_data["house_ownership"],
                land_ownership=form_data["land_ownership"],
                agricultural_activity=form_data["agricultural_activity"],
                business_type=form_data["business_type"],
                vehicle_requirement=form_data["vehicle_requirement"],
                collateral_availability=form_data["collateral_availability"],
                bank_account_status=form_data["bank_account_status"],
                
                # AI Outputs
                top_category=ai_result["top_category"],
                top_score=ai_result["top_score"],
                second_category=top_3[1]["category"] if len(top_3) > 1 else None,
                second_score=top_3[1]["score"] if len(top_3) > 1 else None,
                third_category=top_3[2]["category"] if len(top_3) > 2 else None,
                third_score=top_3[2]["score"] if len(top_3) > 2 else None,
                all_scores_json=json.dumps(ai_result["all_scores"]),
                eligibility_status=ai_result["eligibility"]["status"],
                eligibility_score=ai_result["eligibility"]["eligibility_score"],
                eligibility_details_json=json.dumps(ai_result["eligibility"]),
                recommended_amount_min=ai_result["eligibility"]["recommended_amount_min"],
                recommended_amount_max=ai_result["eligibility"]["recommended_amount_max"],
                suggested_tenure=ai_result["eligibility"]["suggested_tenure"],
                reason_text=ai_result["reason"],
                status="Submitted"
            )

            db.session.add(application)
            db.session.commit()

            flash("AI Loan Detection completed successfully!", "success")
            return redirect(url_for("result", app_id=application.id))

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred while processing your request: {str(e)}", "danger")
            return redirect(url_for("detect_loan"))

    return render_template("detect_loan.html", categories=list(LOAN_CATEGORY_DETAILS.keys()))

@app.route("/result/<int:app_id>")
@login_required
def result(app_id):
    app_record = LoanApplication.query.get_or_404(app_id)
    if app_record.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    all_scores = app_record.get_all_scores()
    eligibility_details = app_record.get_eligibility_details()

    # Fetch matching real-benchmark loan schemes for comparison
    matching_schemes = LoanScheme.query.filter(
        LoanScheme.category.in_([app_record.top_category, app_record.second_category, app_record.third_category]),
        LoanScheme.is_active == True
    ).all()

    # Get required documents checklist for the top loan category
    top_cat_details = LOAN_CATEGORY_DETAILS.get(app_record.top_category, LOAN_CATEGORY_DETAILS["Personal Loan"])
    required_docs = top_cat_details.get("required_documents", [])

    # Fetch already uploaded documents for this application
    uploaded_docs = ApplicationDocument.query.filter_by(application_id=app_record.id).all()
    uploaded_dict = {doc.doc_name: doc for doc in uploaded_docs}

    return render_template(
        "result.html",
        app=app_record,
        all_scores=all_scores,
        eligibility=eligibility_details,
        matching_schemes=matching_schemes,
        required_docs=required_docs,
        uploaded_dict=uploaded_dict,
        top_cat_details=top_cat_details
    )

# -------------------------------------------------------------
# Online Document Submission & Live Camera Scanning API
# -------------------------------------------------------------

@app.route("/api/documents/upload/<int:app_id>", methods=["POST"])
@login_required
def upload_document(app_id):
    app_record = LoanApplication.query.get_or_404(app_id)
    if app_record.user_id != current_user.id and not current_user.is_admin:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    doc_name = request.form.get("doc_name", "").strip()
    doc_category = request.form.get("doc_category", "Verification Document").strip()
    is_camera_scan = request.form.get("is_camera_scan", "false").lower() == "true"
    camera_data_base64 = request.form.get("camera_image_base64")

    if not doc_name:
        return jsonify({"success": False, "error": "Document name is required."}), 400

    # Ensure application folder exists
    app_upload_dir = os.path.join(app.config["UPLOAD_FOLDER"], f"app_{app_id}")
    os.makedirs(app_upload_dir, exist_ok=True)

    unique_prefix = uuid.uuid4().hex[:8]

    # Handle Camera Snapshot (Base64)
    if camera_data_base64 and len(camera_data_base64) > 50:
        try:
            if "," in camera_data_base64:
                header, encoded = camera_data_base64.split(",", 1)
            else:
                encoded = camera_data_base64

            image_bytes = base64.b64decode(encoded)
            file_name = f"scan_{unique_prefix}_{secure_filename(doc_name)}.jpg"
            file_path = os.path.join(app_upload_dir, file_name)
            
            with open(file_path, "wb") as f:
                f.write(image_bytes)

            file_size = len(image_bytes)
            mime_type = "image/jpeg"
            is_camera_scan = True

        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to process camera scan: {str(e)}"}), 500

    # Handle Standard File Upload
    elif "file" in request.files:
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected."}), 400
            
        if not allowed_file(file.filename):
            return jsonify({"success": False, "error": "File type not supported. Allowed: JPG, PNG, PDF."}), 400

        ext = file.filename.rsplit(".", 1)[1].lower()
        file_name = f"doc_{unique_prefix}_{secure_filename(doc_name)}.{ext}"
        file_path = os.path.join(app_upload_dir, file_name)
        file.save(file_path)

        file_size = os.path.getsize(file_path)
        mime_type = file.mimetype or f"image/{ext}" if ext in ["jpg", "jpeg", "png", "webp"] else "application/pdf"

    else:
        return jsonify({"success": False, "error": "No document payload provided."}), 400

    # Check if document already exists for this application (Replacement / Retake)
    existing_doc = ApplicationDocument.query.filter_by(
        application_id=app_id, doc_name=doc_name
    ).first()

    if existing_doc:
        # Remove old physical file if exists
        try:
            if os.path.exists(existing_doc.file_path):
                os.remove(existing_doc.file_path)
        except Exception:
            pass

        existing_doc.file_path = file_path
        existing_doc.file_name = file_name
        existing_doc.file_size = file_size
        existing_doc.mime_type = mime_type
        existing_doc.is_camera_scan = is_camera_scan
        existing_doc.verification_status = "Pending Verification"
        existing_doc.rejection_reason = None
        existing_doc.updated_at = datetime.utcnow()
        doc_record = existing_doc
    else:
        doc_record = ApplicationDocument(
            application_id=app_id,
            doc_name=doc_name,
            doc_category=doc_category,
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type,
            is_camera_scan=is_camera_scan,
            verification_status="Pending Verification"
        )
        db.session.add(doc_record)

    # Update application status if documents submitted
    if app_record.status == "Submitted":
        app_record.status = "Under Review"

    db.session.commit()

    return jsonify({
        "success": True,
        "message": f"'{doc_name}' submitted successfully!",
        "document": {
            "id": doc_record.id,
            "doc_name": doc_record.doc_name,
            "file_name": doc_record.file_name,
            "is_camera_scan": doc_record.is_camera_scan,
            "status": doc_record.verification_status,
            "created_at": doc_record.created_at.strftime("%d %b %Y, %I:%M %p"),
            "preview_url": url_for("preview_document", doc_id=doc_record.id)
        }
    })

@app.route("/api/documents/preview/<int:doc_id>")
@login_required
def preview_document(doc_id):
    doc = ApplicationDocument.query.get_or_404(doc_id)
    app_record = LoanApplication.query.get(doc.application_id)
    
    if app_record.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    dir_path = os.path.dirname(doc.file_path)
    filename = os.path.basename(doc.file_path)
    return send_from_directory(dir_path, filename)

@app.route("/api/documents/delete/<int:doc_id>", methods=["POST"])
@login_required
def delete_document(doc_id):
    doc = ApplicationDocument.query.get_or_404(doc_id)
    app_record = LoanApplication.query.get(doc.application_id)
    
    if app_record.user_id != current_user.id and not current_user.is_admin:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    try:
        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except Exception:
        pass

    db.session.delete(doc)
    db.session.commit()
    return jsonify({"success": True, "message": "Document removed. You can now retake or re-upload."})

# -------------------------------------------------------------
# Admin Management Portal
# -------------------------------------------------------------

def admin_required(f):
    def wrap(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Administrator privileges required.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@app.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    total_apps = LoanApplication.query.count()
    total_users = User.query.filter_by(role="user").count()
    pending_docs = ApplicationDocument.query.filter_by(verification_status="Pending Verification").count()
    verified_docs = ApplicationDocument.query.filter_by(verification_status="Verified").count()
    schemes_count = LoanScheme.query.count()

    recent_apps = LoanApplication.query.order_by(LoanApplication.created_at.desc()).limit(8).all()
    pending_doc_records = ApplicationDocument.query.filter_by(
        verification_status="Pending Verification"
    ).order_by(ApplicationDocument.created_at.desc()).limit(6).all()

    # Category breakdown for charts
    cat_counts = {}
    for cat in LOAN_CATEGORY_DETAILS.keys():
        cnt = LoanApplication.query.filter_by(top_category=cat).count()
        if cnt > 0:
            cat_counts[cat] = cnt

    return render_template(
        "admin/dashboard.html",
        total_apps=total_apps,
        total_users=total_users,
        pending_docs=pending_docs,
        verified_docs=verified_docs,
        schemes_count=schemes_count,
        recent_apps=recent_apps,
        pending_doc_records=pending_doc_records,
        cat_counts=cat_counts
    )

@app.route("/admin/applications")
@login_required
@admin_required
def admin_applications():
    status_filter = request.args.get("status")
    category_filter = request.args.get("category")
    
    query = LoanApplication.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(top_category=category_filter)
        
    applications = query.order_by(LoanApplication.created_at.desc()).all()
    return render_template(
        "admin/applications.html",
        applications=applications,
        categories=list(LOAN_CATEGORY_DETAILS.keys()),
        current_status=status_filter,
        current_category=category_filter
    )

@app.route("/admin/application/<int:app_id>")
@login_required
@admin_required
def admin_view_application(app_id):
    app_record = LoanApplication.query.get_or_404(app_id)
    documents = ApplicationDocument.query.filter_by(application_id=app_id).all()
    all_scores = app_record.get_all_scores()
    eligibility = app_record.get_eligibility_details()
    
    return render_template(
        "admin/view_application.html",
        app=app_record,
        documents=documents,
        all_scores=all_scores,
        eligibility=eligibility
    )

@app.route("/admin/document/verify/<int:doc_id>", methods=["POST"])
@login_required
@admin_required
def admin_verify_document(doc_id):
    doc = ApplicationDocument.query.get_or_404(doc_id)
    action = request.form.get("action")  # 'verify' or 'reject'
    reason = request.form.get("reason", "").strip()

    if action == "verify":
        doc.verification_status = "Verified"
        doc.rejection_reason = None
    elif action == "reject":
        doc.verification_status = "Rejected"
        doc.rejection_reason = reason or "Document image is blurred or details do not match applicant profile."
    else:
        return jsonify({"success": False, "error": "Invalid action"}), 400

    doc.verified_by = current_user.name
    doc.verified_at = datetime.utcnow()
    db.session.commit()

    flash(f"Document '{doc.doc_name}' marked as {doc.verification_status}.", "success")
    return redirect(url_for("admin_view_application", app_id=doc.application_id))

@app.route("/admin/application/update-status/<int:app_id>", methods=["POST"])
@login_required
@admin_required
def admin_update_app_status(app_id):
    app_record = LoanApplication.query.get_or_404(app_id)
    new_status = request.form.get("status")
    admin_notes = request.form.get("admin_notes", "").strip()

    if new_status in ["Submitted", "Under Review", "Verified", "Approved", "Rejected"]:
        app_record.status = new_status
        if admin_notes:
            app_record.admin_notes = admin_notes
        db.session.commit()
        flash(f"Application status updated to {new_status}.", "success")

    return redirect(url_for("admin_view_application", app_id=app_id))

@app.route("/admin/schemes", methods=["GET", "POST"])
@login_required
@admin_required
def admin_schemes():
    if request.method == "POST":
        category = request.form.get("category")
        bank_name = request.form.get("bank_name")
        scheme_name = request.form.get("scheme_name")
        interest_rate_min = float(request.form.get("interest_rate_min", 8.0))
        interest_rate_max = float(request.form.get("interest_rate_max", 12.0))
        max_amount = float(request.form.get("max_amount", 1000000))
        max_tenure_months = int(request.form.get("max_tenure_months", 60))
        processing_fee = request.form.get("processing_fee", "1.0%")
        eligibility_summary = request.form.get("eligibility_summary", "")
        required_docs_summary = request.form.get("required_docs_summary", "")

        scheme = LoanScheme(
            category=category,
            bank_name=bank_name,
            scheme_name=scheme_name,
            interest_rate_min=interest_rate_min,
            interest_rate_max=interest_rate_max,
            max_amount=max_amount,
            max_tenure_months=max_tenure_months,
            processing_fee=processing_fee,
            eligibility_summary=eligibility_summary,
            required_docs_summary=required_docs_summary,
            is_active=True
        )
        db.session.add(scheme)
        db.session.commit()
        flash("New loan scheme added successfully!", "success")
        return redirect(url_for("admin_schemes"))

    schemes = LoanScheme.query.order_by(LoanScheme.category, LoanScheme.bank_name).all()
    return render_template("admin/schemes.html", schemes=schemes, categories=list(LOAN_CATEGORY_DETAILS.keys()))

@app.route("/admin/users")
@login_required
@admin_required
def admin_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)

# -------------------------------------------------------------
# Quick Demo Profiles API (For testing convenience)
# -------------------------------------------------------------

@app.route("/api/demo-profile/<profile_type>")
def get_demo_profile(profile_type):
    """
    Returns prefilled demographic & financial data for one-click testing in the UI.
    Profiles: 'farmer', 'student', 'salaried_home', 'woman_entrepreneur', 'business_owner'
    """
    profiles = {
        "farmer": {
            "full_name": "Ramesh Patel",
            "age": 42,
            "gender": "Male",
            "mobile": "9820011223",
            "state": "Maharashtra",
            "district": "Nashik",
            "city_village": "Yeola Village",
            "occupation": "Farmer",
            "monthly_income": 30000,
            "annual_income": 360000,
            "employment_type": "Agriculture / Farming",
            "company_name": "Self-Cultivation Farm",
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
        },
        "student": {
            "full_name": "Priya Sharma",
            "age": 21,
            "gender": "Female",
            "mobile": "9876501234",
            "state": "Karnataka",
            "district": "Bengaluru Urban",
            "city_village": "Bengaluru",
            "occupation": "Student",
            "monthly_income": 0,
            "annual_income": 0,
            "employment_type": "Student / Unemployed",
            "company_name": "N/A",
            "credit_score": 700,
            "existing_loans": 0,
            "existing_emi": 0,
            "loan_amount": 750000,
            "loan_purpose": "Professional courses (Medical/Engg/MBA)",
            "loan_tenure": 60,
            "education_status": "Undergraduate",
            "applicant_persona": "Student",
            "house_ownership": "Rented",
            "land_ownership": "No",
            "agricultural_activity": "None",
            "business_type": "None",
            "vehicle_requirement": "None",
            "collateral_availability": "None",
            "bank_account_status": "Active Savings Account"
        },
        "salaried_home": {
            "full_name": "Vikram Adve",
            "age": 34,
            "gender": "Male",
            "mobile": "9911223344",
            "state": "Telangana",
            "district": "Hyderabad",
            "city_village": "Gachibowli, Hyderabad",
            "occupation": "Salaried",
            "monthly_income": 125000,
            "annual_income": 1500000,
            "employment_type": "Full-Time Salaried",
            "company_name": "Infosys Ltd",
            "credit_score": 780,
            "existing_loans": 1,
            "existing_emi": 12000,
            "loan_amount": 4500000,
            "loan_purpose": "Buying a flat / apartment",
            "loan_tenure": 240,
            "education_status": "Postgraduate",
            "applicant_persona": "Working",
            "house_ownership": "Rented",
            "land_ownership": "No",
            "agricultural_activity": "None",
            "business_type": "None",
            "vehicle_requirement": "None",
            "collateral_availability": "Property / Land",
            "bank_account_status": "Salary Account"
        },
        "woman_entrepreneur": {
            "full_name": "Ananya Sen",
            "age": 31,
            "gender": "Female",
            "mobile": "9748012345",
            "state": "West Bengal",
            "district": "Kolkata",
            "city_village": "Salt Lake, Kolkata",
            "occupation": "Homemaker / Self-employed Woman",
            "monthly_income": 45000,
            "annual_income": 540000,
            "employment_type": "Self-Employed",
            "company_name": "Ananya Designer Boutique & Handicrafts",
            "credit_score": 735,
            "existing_loans": 0,
            "existing_emi": 0,
            "loan_amount": 500000,
            "loan_purpose": "Women entrepreneur venture",
            "loan_tenure": 36,
            "education_status": "Graduate",
            "applicant_persona": "Business",
            "house_ownership": "Owned",
            "land_ownership": "No",
            "agricultural_activity": "None",
            "business_type": "Home-based Enterprise",
            "vehicle_requirement": "None",
            "collateral_availability": "None",
            "bank_account_status": "Current Account"
        },
        "business_owner": {
            "full_name": "Rajesh Gupta",
            "age": 45,
            "gender": "Male",
            "mobile": "9810055443",
            "state": "Gujarat",
            "district": "Ahmedabad",
            "city_village": "Naroda Industrial Area",
            "occupation": "Business Owner",
            "monthly_income": 180000,
            "annual_income": 2160000,
            "employment_type": "Business Enterprise",
            "company_name": "Gupta Engineering Works",
            "credit_score": 760,
            "existing_loans": 1,
            "existing_emi": 25000,
            "loan_amount": 2500000,
            "loan_purpose": "Commercial machinery purchase",
            "loan_tenure": 48,
            "education_status": "Graduate",
            "applicant_persona": "Business",
            "house_ownership": "Owned",
            "land_ownership": "Yes",
            "agricultural_activity": "None",
            "business_type": "Manufacturing",
            "vehicle_requirement": "Commercial Vehicle",
            "collateral_availability": "Machinery / Stock",
            "bank_account_status": "Current Account"
        }
    }
    return jsonify(profiles.get(profile_type, {}))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
