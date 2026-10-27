"""
AI Model Training for AI-Based Loan Detection and Recommendation System.
Trains a Scikit-learn Pipeline with Feature Scaling, One-Hot Encoding,
and Random Forest Classifier for loan category detection.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from dataset_generator import generate_dataset, LOAN_CATEGORIES

def train_and_save_model(data_path=None, model_path="loan_classifier_pipeline.joblib"):
    print("=" * 60)
    print("AI LOAN CLASSIFIER MODEL TRAINING PIPELINE")
    print("=" * 60)
    
    if data_path and os.path.exists(data_path):
        print(f"Loading dataset from {data_path}...")
        df = pd.read_csv(data_path)
    else:
        print("Generating synthetic 8,500-sample balanced dataset...")
        df = generate_dataset(num_samples=8500)
        df.to_csv("loan_applicants_dataset.csv", index=False)
        print("Dataset generated and saved to loan_applicants_dataset.csv")

    # Features and Target
    target_col = "loan_category"
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # Identify feature types
    numeric_features = [
        "age", "monthly_income", "annual_income", "credit_score",
        "existing_loans", "existing_emi", "loan_amount", "loan_tenure"
    ]
    
    categorical_features = [
        "gender", "occupation", "employment_type", "loan_purpose",
        "education_status", "applicant_persona", "house_ownership",
        "land_ownership", "agricultural_activity", "business_type",
        "vehicle_requirement", "collateral_availability", "bank_account_status"
    ]
    
    print(f"Features: {len(numeric_features)} numerical, {len(categorical_features)} categorical.")
    print(f"Target classes ({len(LOAN_CATEGORIES)}): {LOAN_CATEGORIES}")

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"Training samples: {len(X_train)}, Testing samples: {len(X_test)}")

    # Preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features)
        ]
    )

    # Full Model Pipeline using Random Forest Classifier
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(
                n_estimators=150,
                max_depth=20,
                min_samples_split=4,
                min_samples_leaf=2,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1
            ))
        ]
    )

    print("Training RandomForest model pipeline...")
    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy on Test Set: {acc * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=pipeline.classes_))

    # Save artifact
    metadata = {
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "classes": list(pipeline.classes_),
        "accuracy": float(acc)
    }
    
    saved_bundle = {
        "pipeline": pipeline,
        "metadata": metadata
    }
    
    joblib.dump(saved_bundle, model_path)
    print(f"Trained model bundle successfully saved to '{model_path}'.")
    return pipeline, metadata

if __name__ == "__main__":
    train_and_save_model()
