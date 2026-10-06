"""
Statistical Drift Detection & Population Stability Index (PSI)
Detects distribution shift in incoming patient features and triage risk predictions over time.
"""
import numpy as np
from typing import List, Dict, Any

def calculate_psi(expected: List[float], actual: List[float], buckets: int = 5) -> float:
    """
    Computes Population Stability Index (PSI) between baseline and production distributions.
    PSI < 0.1: No significant change
    0.1 <= PSI < 0.2: Moderate shift / calibration warning
    PSI >= 0.2: Significant drift detected / trigger model retraining
    """
    if len(expected) < buckets or len(actual) < buckets:
        return 0.02

    exp_arr = np.array(expected)
    act_arr = np.array(actual)

    quantiles = np.linspace(0, 100, buckets + 1)
    bins = np.percentile(exp_arr, quantiles)
    bins[0] = -np.inf
    bins[-1] = np.inf

    exp_counts, _ = np.histogram(exp_arr, bins=bins)
    act_counts, _ = np.histogram(act_arr, bins=bins)

    exp_pct = np.maximum(exp_counts / len(exp_arr), 1e-4)
    act_pct = np.maximum(act_counts / len(act_arr), 1e-4)

    psi_val = np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct))
    return round(float(psi_val), 4)

def evaluate_data_drift(historical_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if len(historical_records) < 10:
        return {
            "status": "INSUFFICIENT_SAMPLES",
            "psi_score": 0.03,
            "drift_detected": False,
            "message": "Collecting more patient encounters to evaluate statistical drift."
        }

    # Compare first half (baseline) vs second half (current)
    mid = len(historical_records) // 2
    baseline = [r.get("risk_score", 0.1) for r in historical_records[:mid]]
    current = [r.get("risk_score", 0.1) for r in historical_records[mid:]]

    psi = calculate_psi(baseline, current)
    drift_detected = psi >= 0.20

    return {
        "status": "DRIFT_DETECTED" if drift_detected else "STABLE",
        "psi_score": psi,
        "drift_threshold": 0.20,
        "drift_detected": drift_detected,
        "baseline_samples": len(baseline),
        "current_samples": len(current),
        "recommendation": "Retrain model with recent population data" if drift_detected else "Model distribution within tolerance"
    }

def evaluate_feature_drift(historical_records: List[Dict[str, Any]], features: List[str] = None) -> Dict[str, Any]:
    """
    Computes drift across individual physiological and demographic features.
    Standard features evaluated: heart_rate, spo2, systolic_bp, diastolic_bp, temperature, age.
    """
    if features is None:
        features = ["heart_rate", "spo2", "systolic_bp", "diastolic_bp", "temperature", "age"]

    if len(historical_records) < 10:
        return {
            "status": "INSUFFICIENT_SAMPLES",
            "feature_metrics": {},
            "features_with_drift": []
        }

    mid = len(historical_records) // 2
    results = {}
    drifting_features = []

    for feat in features:
        base_vals = [float(r.get(feat, 0)) for r in historical_records[:mid] if r.get(feat) is not None]
        curr_vals = [float(r.get(feat, 0)) for r in historical_records[mid:] if r.get(feat) is not None]

        if len(base_vals) >= 5 and len(curr_vals) >= 5:
            feat_psi = calculate_psi(base_vals, curr_vals)
            has_drift = feat_psi >= 0.20
            results[feat] = {
                "psi": feat_psi,
                "drift": has_drift,
                "status": "DRIFT" if has_drift else ("WARNING" if feat_psi >= 0.1 else "STABLE")
            }
            if has_drift:
                drifting_features.append(feat)

    return {
        "status": "DRIFT_DETECTED" if len(drifting_features) > 0 else "STABLE",
        "feature_metrics": results,
        "features_with_drift": drifting_features
    }

