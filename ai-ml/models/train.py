"""
AI/ML Training Pipeline for Triage Risk Classification
Generates a representative clinical triage training dataset, trains a Logistic Regression model,
and persists the trained model artifact with joblib.
"""
import os
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "triage_model.joblib")

# Feature Vector format:
# [spo2, pulse, temp, age, has_chest_pain, has_sob, has_high_fever, has_fainting, has_severe_headache, has_cough, is_rural]
FEATURE_NAMES = [
    "spo2", "pulse", "temperature", "age",
    "chest_pain", "shortness_of_breath", "high_fever",
    "fainting", "severe_headache", "cough", "is_rural"
]

def generate_synthetic_triage_data(n_samples=2500):
    np.random.seed(42)
    X = []
    y = []

    for _ in range(n_samples):
        spo2 = np.random.uniform(85, 100)
        pulse = np.random.uniform(45, 140)
        temp = np.random.uniform(97.0, 104.5)
        age = np.random.uniform(1, 85)

        has_cp = 1 if np.random.rand() < 0.20 else 0
        has_sob = 1 if np.random.rand() < 0.25 else 0
        has_hf = 1 if np.random.rand() < 0.18 else 0
        has_faint = 1 if np.random.rand() < 0.12 else 0
        has_sh = 1 if np.random.rand() < 0.15 else 0
        has_cough = 1 if np.random.rand() < 0.35 else 0
        is_rural = 1 if np.random.rand() < 0.60 else 0

        # Clinical triage severity score formula
        risk_score = 0.05
        if spo2 < 92:
            risk_score += 0.40
        elif spo2 < 95:
            risk_score += 0.15

        if pulse > 120 or pulse < 50:
            risk_score += 0.20
        if temp > 102.0:
            risk_score += 0.15
        if has_cp:
            risk_score += 0.35
        if has_sob:
            risk_score += 0.30
        if has_hf:
            risk_score += 0.20
        if has_faint:
            risk_score += 0.25
        if has_sh:
            risk_score += 0.10
        if has_cough:
            risk_score += 0.05

        # Target label: 0=Low, 1=Medium, 2=High, 3=Emergency
        if risk_score >= 0.70:
            label = 3
        elif risk_score >= 0.45:
            label = 2
        elif risk_score >= 0.25:
            label = 1
        else:
            label = 0

        X.append([spo2, pulse, temp, age, has_cp, has_sob, has_hf, has_faint, has_sh, has_cough, is_rural])
        y.append(label)

    return np.array(X), np.array(y)

def train_and_persist_model():
    print("[AI/ML] Generating clinical triage training dataset...")
    X, y = generate_synthetic_triage_data()

    print("[AI/ML] Fitting Logistic Regression Clinical Model...")
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=1000, random_state=42))
    ])
    pipeline.fit(X, y)

    bundle = {
        "pipeline": pipeline,
        "feature_names": FEATURE_NAMES,
        "classes": ["LOW", "MEDIUM", "HIGH", "EMERGENCY"],
        "version": "1.0.0"
    }

    joblib.dump(bundle, MODEL_PATH)

    # Also save in ai_ml/models if present
    alt_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "ai_ml", "models"))
    if os.path.exists(alt_dir):
        joblib.dump(bundle, os.path.join(alt_dir, "triage_model.joblib"))

    print(f"[AI/ML] Model successfully trained and saved to: {MODEL_PATH}")
    return MODEL_PATH

if __name__ == "__main__":
    train_and_persist_model()
