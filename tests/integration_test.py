"""
Comprehensive End-to-End Test Suite for Ayushman Bharat Healthtech Platform
"""
import unittest
import time
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, BASE_DIR)

from shared.security import hash_password, verify_password, create_jwt_token, decode_jwt_token
from shared.schemas import UserRole
from shared.db import (
    init_database, record_login_attempt, is_user_locked_out,
    get_db_connection, revoke_token_in_db, is_token_revoked_in_db
)
from services.core_backend.patients.service import (
    validate_abha_id, create_patient_record, get_patient_by_id, toggle_patient_consent_status
)
from services.core_backend.providers.service import get_all_providers_list
from services.core_backend.records.service import create_ehr_record, get_records_by_patient
from services.core_backend.scheduling.service import book_appointment, get_patient_appointments
from ai_ml.monitoring.app import predict_triage_risk, calculate_fairness_metrics
from ai_ml.drift_detection.psi import calculate_psi, evaluate_data_drift
from services.api_gateway.fhir.mapper import to_fhir_patient, to_fhir_observation
from services.api_gateway.snomed_mapping.lookup import lookup_snomed_concept
from services.api_gateway.cda_parser.parser import parse_ccda_xml
from services.api_gateway.external_provider_sync.abdm_sync import sync_abha_record_to_sandbox
from services.audit_logging.main import append_audit_event, verify_audit_ledger_db, calculate_hash

class AyushmanBharatModernizedPlatformTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_database()

    def test_01_security_bcrypt_and_pyjwt(self):
        pw = "SuperSecurePassword123"
        hashed = hash_password(pw)
        self.assertTrue(verify_password(pw, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

        payload = {"sub": "doctor1", "role": UserRole.CLINICIAN, "full_name": "Dr. Priya Sen"}
        token = create_jwt_token(payload, expires_delta=3600)
        self.assertIsNotNone(token)

        decoded = decode_jwt_token(token)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["sub"], "doctor1")
        self.assertEqual(decoded["role"], UserRole.CLINICIAN)

    def test_02_persistent_login_rate_limiting_and_revocation(self):
        ident = f"test_user_lockout_{int(time.time()*1000)}"
        for _ in range(5):
            record_login_attempt(ident, success=False)
        self.assertTrue(is_user_locked_out(ident))

        test_token = f"dummy-token-revocation-{int(time.time()*1000)}"
        self.assertFalse(is_token_revoked_in_db(test_token))
        revoke_token_in_db(test_token)
        self.assertTrue(is_token_revoked_in_db(test_token))

    def test_03_patient_abha_validation_and_crud(self):
        self.assertTrue(validate_abha_id("14-8899-2341-9988"))
        self.assertTrue(validate_abha_id("14889923419988"))
        self.assertFalse(validate_abha_id("invalid-abha-123"))

        unique_abha = f"14-{int(time.time()*100)%9000+1000}-7766-5544"
        patient = create_patient_record({
            "name": "Kavita Devi",
            "age": 39,
            "gender": "female",
            "region": "rural",
            "state": "Odisha",
            "abha_id": unique_abha,
            "active_conditions": ["Mild Anaemia"]
        })
        self.assertIsNotNone(patient)
        self.assertEqual(patient["name"], "Kavita Devi")
        
        # Toggle consent
        new_state = toggle_patient_consent_status(patient["patient_id"])
        self.assertEqual(new_state, False)

    def test_04_providers_and_ehr_storage(self):
        providers = get_all_providers_list()
        self.assertGreater(len(providers), 0)

        ehr = create_ehr_record("P-101", "Prescription", "Hypertension Medication", "Amlodipine 5mg once daily", "Oral administration")
        self.assertIsNotNone(ehr["record_id"])
        self.assertIsNotNone(ehr["document_hash"])

        patient_records = get_records_by_patient("P-101")
        self.assertGreater(len(patient_records), 0)

    def test_05_scheduling_and_conflict_handling(self):
        provider_id = "PR-01"
        slot = f"Slot-{int(time.time()*1000)}"
        
        apt = book_appointment("P-101", provider_id, slot, "Routine checkup")
        self.assertEqual(apt["status"], "CONFIRMED")

        # Conflict expectation
        with self.assertRaises(ValueError):
            book_appointment("P-102", provider_id, slot, "Conflicting appointment")

    def test_06_ai_ml_triage_explainability_and_drift(self):
        res = predict_triage_risk(
            symptoms=["chest_pain", "shortness_of_breath"],
            vitals={"spo2": 89, "pulse": 125, "temperature": 99.1},
            demographics={"gender": "female", "region": "rural", "age": 52}
        )
        self.assertIn(res["risk_level"], ["HIGH", "EMERGENCY"])
        self.assertGreaterEqual(res["risk_score"], 0.70)
        self.assertTrue(len(res["explainability"]["top_factors"]) >= 2)

        metrics = calculate_fairness_metrics()
        self.assertTrue(metrics["disparate_impact_passed"])

        # Test PSI calculation
        psi = calculate_psi([0.1, 0.2, 0.3, 0.4, 0.5], [0.12, 0.22, 0.28, 0.41, 0.52])
        self.assertLess(psi, 0.20)

    def test_07_interoperability_fhir_snomed_cda_abdm(self):
        p_fhir = to_fhir_patient({"patient_id": "P-101", "name": "Aarav Sharma", "abha_id": "14-8899-2341-9988", "gender": "male"})
        self.assertEqual(p_fhir["resourceType"], "Patient")

        snomed = lookup_snomed_concept("chest pain")
        self.assertIsNotNone(snomed)
        self.assertEqual(snomed["conceptId"], "29857009")

        cda_res = parse_ccda_xml("<ClinicalDocument xmlns='urn:hl7-org:v3'><title>Test CDA</title></ClinicalDocument>")
        self.assertEqual(cda_res["status"], "PARSED_SUCCESS")

        abdm_res = sync_abha_record_to_sandbox("14-8899-2341-9988", {"test": True})
        self.assertEqual(abdm_res["status"], "SYNCED_TO_ABDM_SANDBOX")

    def test_08_cryptographic_audit_ledger(self):
        verification = verify_audit_ledger_db()
        self.assertTrue(verification["ledger_valid"])
        self.assertEqual(len(verification["tampered_records"]), 0)

        evt = append_audit_event("TEST_ACTION", "doctor1", "CLINICIAN", "P-101", "EHR_ACCESS", {"viewed": True})
        self.assertEqual(evt["record_hash"], calculate_hash(evt))

if __name__ == "__main__":
    unittest.main()
