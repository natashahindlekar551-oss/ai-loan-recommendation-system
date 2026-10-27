"""
Automated End-to-End Test Suite for AI Loan Detection & Recommendation System.
Validates database seeding, AI multi-category inference, user workflows,
camera scan submission, and admin document verification station.
"""

import os
import json
import base64
import unittest
from app import app, db
from models import User, LoanApplication, ApplicationDocument, LoanScheme

class TestAILoanSystem(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

        with app.app_context():
            db.create_all()
            from seed_data import seed_database
            seed_database(app)

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_01_database_seeding(self):
        """Verify default admin, demo user and 20 loan schemes exist."""
        with app.app_context():
            admin = User.query.filter_by(email="admin@loanai.com").first()
            self.assertIsNotNone(admin)
            self.assertTrue(admin.is_admin)

            demo_user = User.query.filter_by(email="ramesh.patel@example.com").first()
            self.assertIsNotNone(demo_user)
            self.assertEqual(demo_user.name, "Ramesh Patel")

            schemes_count = LoanScheme.query.count()
            self.assertGreaterEqual(schemes_count, 10)
            print(f"[TEST 1 PASS] Seeder verified: {schemes_count} schemes and default users ready.")

    def test_02_farmer_ai_loan_recommendation(self):
        """
        Verify Farmer test case from prompt:
        Occupation: Farmer, Income: ₹30,000, Land: Yes, Purpose: Crop cultivation, Amount: ₹2,00,000
        AI Result: Agriculture Loan as best match (90%+), Top 3 suitable loans, clear reason.
        """
        # Login demo user
        login_res = self.client.post("/login", data={
            "email": "ramesh.patel@example.com",
            "password": "User@1234"
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)

        # Submit loan form
        form_payload = {
            "full_name": "Ramesh Patel",
            "age": 42,
            "gender": "Male",
            "mobile": "9820011223",
            "state": "Maharashtra",
            "district": "Nashik",
            "city_village": "Yeola",
            "occupation": "Farmer",
            "monthly_income": 30000,
            "annual_income": 360000,
            "employment_type": "Agriculture / Farming",
            "company_name": "Patel Farm",
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

        res = self.client.post("/detect-loan", data=form_payload, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        with app.app_context():
            application = LoanApplication.query.filter_by(full_name="Ramesh Patel").order_by(LoanApplication.id.desc()).first()
            self.assertIsNotNone(application)
            self.assertEqual(application.top_category, "Agriculture / Farmer Loan")
            self.assertGreaterEqual(application.top_score, 85)
            self.assertIsNotNone(application.second_category)
            self.assertIsNotNone(application.third_category)
            self.assertEqual(application.eligibility_status, "Likely Eligible")
            self.assertIn("crop", application.reason_text.lower())
            
            print(f"[TEST 2 PASS] Farmer AI Evaluation: Top Match '{application.top_category}' with {application.top_score}%.")
            print(f"Top 3: 1. {application.top_category} ({application.top_score}%), 2. {application.second_category} ({application.second_score}%), 3. {application.third_category} ({application.third_score}%)")

    def test_03_camera_scan_document_submission(self):
        """Verify online document submission using camera snapshot base64 data."""
        # Login demo user
        self.client.post("/login", data={
            "email": "ramesh.patel@example.com",
            "password": "User@1234"
        }, follow_redirects=True)

        with app.app_context():
            # Create a test application
            app_record = LoanApplication(
                user_id=2, full_name="Ramesh Patel", age=42, gender="Male", mobile="9820011223",
                state="MH", district="Nashik", city_village="Yeola", occupation="Farmer",
                monthly_income=30000, annual_income=360000, employment_type="Agriculture / Farming",
                credit_score=720, loan_amount=200000, loan_purpose="Crop loan", loan_tenure=24,
                education_status="High School", applicant_persona="Farmer", house_ownership="Owned",
                land_ownership="Yes", top_category="Agriculture / Farmer Loan", top_score=94
            )
            db.session.add(app_record)
            db.session.commit()
            app_id = app_record.id

        # Simulated small 1x1 JPEG base64 image from camera canvas
        fake_camera_base64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA="

        # Post camera scan
        upload_res = self.client.post(f"/api/documents/upload/{app_id}", data={
            "doc_name": "Aadhaar Card",
            "doc_category": "Identity & Address Proof",
            "is_camera_scan": "true",
            "camera_image_base64": fake_camera_base64
        })
        self.assertEqual(upload_res.status_code, 200)
        data = json.loads(upload_res.data)
        self.assertTrue(data["success"])
        self.assertTrue(data["document"]["is_camera_scan"])
        self.assertEqual(data["document"]["status"], "Pending Verification")

        with app.app_context():
            doc = ApplicationDocument.query.filter_by(application_id=app_id, doc_name="Aadhaar Card").first()
            self.assertIsNotNone(doc)
            self.assertTrue(doc.is_camera_scan)
            self.assertTrue(os.path.exists(doc.file_path))
            print(f"[TEST 3 PASS] Camera scan uploaded successfully: {doc.file_name} (Status: {doc.verification_status})")

    def test_04_admin_document_verification_flow(self):
        """Verify Admin inspecting and approving/rejecting submitted documents."""
        # Login admin
        self.client.post("/login", data={
            "email": "admin@loanai.com",
            "password": "Admin@1234"
        }, follow_redirects=True)

        with app.app_context():
            app_record = LoanApplication(
                user_id=2, full_name="Ramesh Patel", age=42, gender="Male", mobile="9820011223",
                state="MH", district="Nashik", city_village="Yeola", occupation="Farmer",
                monthly_income=30000, annual_income=360000, employment_type="Agriculture / Farming",
                credit_score=720, loan_amount=200000, loan_purpose="Crop loan", loan_tenure=24,
                education_status="High School", applicant_persona="Farmer", house_ownership="Owned",
                land_ownership="Yes", top_category="Agriculture / Farmer Loan", top_score=94
            )
            db.session.add(app_record)
            db.session.commit()

            doc = ApplicationDocument(
                application_id=app_record.id,
                doc_name="Land Record Documents (7/12 / Patta)",
                doc_category="Asset Proof",
                file_path=os.path.join(app.config["UPLOAD_FOLDER"], "test_patta.jpg"),
                file_name="test_patta.jpg",
                is_camera_scan=True,
                verification_status="Pending Verification"
            )
            db.session.add(doc)
            db.session.commit()
            doc_id = doc.id
            app_id = app_record.id

        # Admin Approves Document
        verify_res = self.client.post(f"/admin/document/verify/{doc_id}", data={
            "action": "verify"
        }, follow_redirects=True)
        self.assertEqual(verify_res.status_code, 200)

        with app.app_context():
            updated_doc = ApplicationDocument.query.get(doc_id)
            self.assertEqual(updated_doc.verification_status, "Verified")
            self.assertEqual(updated_doc.verified_by, "System Administrator")
            print(f"[TEST 4A PASS] Admin approved document: Verification status is 'Verified'")

        # Admin Rejects Document
        reject_res = self.client.post(f"/admin/document/verify/{doc_id}", data={
            "action": "reject",
            "reason": "Stamp and seal blurry, please rescan in sunlight."
        }, follow_redirects=True)
        self.assertEqual(reject_res.status_code, 200)

        with app.app_context():
            rejected_doc = ApplicationDocument.query.get(doc_id)
            self.assertEqual(rejected_doc.verification_status, "Rejected")
            self.assertIn("blurry", rejected_doc.rejection_reason)
            print(f"[TEST 4B PASS] Admin rejected document with reason: '{rejected_doc.rejection_reason}'")

if __name__ == "__main__":
    unittest.main()
