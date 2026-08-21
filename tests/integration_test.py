"""
End-to-End Integration Tests for Ayushman Bharat Healthtech Platform
Uses importlib to load modules from hyphenated directories cleanly.
"""
import unittest
import time
import os
import sys
import importlib.util

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

def load_module_from_path(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Load services
shared_schemas = load_module_from_path("shared_schemas", os.path.join(BASE_DIR, "shared", "schemas.py"))
auth_svc = load_module_from_path("auth_svc", os.path.join(BASE_DIR, "services", "auth-service", "main.py"))
audit_svc = load_module_from_path("audit_svc", os.path.join(BASE_DIR, "services", "audit-logging", "main.py"))
aiml_svc = load_module_from_path("aiml_svc", os.path.join(BASE_DIR, "ai-ml", "monitoring", "app.py"))
fairness_eval = load_module_from_path("fairness_eval", os.path.join(BASE_DIR, "ai-ml", "evaluation", "fairness_evaluator.py"))

UserRole = shared_schemas.UserRole
create_jwt = auth_svc.create_jwt
verify_jwt = auth_svc.verify_jwt
predict_triage_risk = aiml_svc.predict_triage_risk
calculate_fairness_metrics = aiml_svc.calculate_fairness_metrics
evaluate_disparate_impact = fairness_eval.evaluate_disparate_impact
append_audit_event = audit_svc.append_audit_event
calculate_hash = audit_svc.calculate_hash
verify_audit_ledger_db = audit_svc.verify_audit_ledger_db

class HealthtechPlatformIntegrationTests(unittest.TestCase):

    def test_01_auth_token_issuance_and_claims(self):
        claims = {
            "sub": "doctor1",
            "role": UserRole.CLINICIAN,
            "full_name": "Dr. Priya Sen",
            "exp": time.time() + 3600
        }
        token = create_jwt(claims)
        self.assertIsNotNone(token)
        self.assertEqual(len(token.split(".")), 3)

        verified = verify_jwt(token)
        self.assertIsNotNone(verified)
        self.assertEqual(verified["sub"], "doctor1")
        self.assertEqual(verified["role"], UserRole.CLINICIAN)

    def test_02_ai_triage_risk_prediction_and_explainability(self):
        res = predict_triage_risk(
            symptoms=["chest_pain", "shortness_of_breath"],
            vitals={"spo2": 90, "pulse": 115, "temperature": 99.2},
            demographics={"gender": "female", "region": "rural", "age": 48}
        )
        self.assertIn(res["risk_level"], ["HIGH", "EMERGENCY"])
        self.assertGreaterEqual(res["risk_score"], 0.70)
        self.assertTrue(len(res["explainability"]["top_factors"]) >= 2)

    def test_03_algorithmic_fairness_four_fifths_rule(self):
        dataset = [
            {"demographics": {"region": "rural"}, "is_high_risk": True},
            {"demographics": {"region": "rural"}, "is_high_risk": False},
            {"demographics": {"region": "urban"}, "is_high_risk": True},
            {"demographics": {"region": "urban"}, "is_high_risk": False}
        ]
        report = evaluate_disparate_impact(dataset, protected_attribute="region")
        self.assertTrue(report["four_fifths_rule_passed"])
        self.assertGreaterEqual(report["demographic_parity_ratio"], 0.80)

    def test_06_database_audit_chain_tamper_verification(self):
        v = audit_svc.verify_audit_ledger_db()
        self.assertTrue(v["ledger_valid"])
        self.assertGreater(v["chain_length"], 0)
        self.assertEqual(len(v["tampered_records"]), 0)

        # Append new event
        evt = audit_svc.append_audit_event("TEST_ENCOUNTER", "doctor1", "CLINICIAN", "P-101", "FHIR_ENCOUNTER", {"test": True})
        self.assertEqual(evt["record_hash"], audit_svc.calculate_hash(evt))

        v2 = audit_svc.verify_audit_ledger_db()
        self.assertTrue(v2["ledger_valid"])
        self.assertEqual(v2["chain_length"], v["chain_length"] + 1)

if __name__ == "__main__":
    unittest.main()
