"""
Unit Tests for FHIR R4 and SNOMED CT Mapping Services
"""
import unittest
from services.api_gateway.fhir.mapper import (
    to_fhir_patient,
    to_fhir_observation,
    to_fhir_condition,
    to_fhir_encounter,
    to_fhir_bundle
)
from services.api_gateway.snomed_mapping.lookup import (
    lookup_snomed_concept,
    search_snomed_concepts,
    batch_map_terms
)

class TestFhirAndSnomedMapping(unittest.TestCase):

    def test_fhir_patient_mapping(self):
        pat_data = {
            "patient_id": "P-1001",
            "abha_id": "14-9999-8888-7777",
            "name": "Aarav Sharma",
            "gender": "male",
            "state": "Odisha",
            "region": "rural",
            "preferred_language": "or"
        }
        res = to_fhir_patient(pat_data)
        self.assertEqual(res["resourceType"], "Patient")
        self.assertEqual(res["id"], "P-1001")
        self.assertEqual(res["identifier"][0]["value"], "14-9999-8888-7777")
        self.assertEqual(res["name"][0]["text"], "Aarav Sharma")
        self.assertEqual(res["communication"][0]["language"]["coding"][0]["code"], "or")

    def test_fhir_observation_mapping(self):
        obs = to_fhir_observation("8867-4", "Heart rate", 76, "beats/min", "P-1001")
        self.assertEqual(obs["resourceType"], "Observation")
        self.assertEqual(obs["status"], "final")
        self.assertEqual(obs["valueQuantity"]["value"], 76)
        self.assertEqual(obs["subject"]["reference"], "Patient/P-1001")

    def test_fhir_condition_mapping(self):
        cond = to_fhir_condition("C-501", "38341003", "Hypertensive disorder", "P-1001")
        self.assertEqual(cond["resourceType"], "Condition")
        self.assertEqual(cond["code"]["coding"][0]["code"], "38341003")
        self.assertEqual(cond["clinicalStatus"]["coding"][0]["code"], "active")

    def test_fhir_encounter_and_bundle(self):
        enc = to_fhir_encounter("E-901", "P-1001")
        self.assertEqual(enc["resourceType"], "Encounter")
        self.assertEqual(enc["class"]["code"], "AMB")

        bundle = to_fhir_bundle("B-100", [enc])
        self.assertEqual(bundle["resourceType"], "Bundle")
        self.assertEqual(bundle["total"], 1)
        self.assertEqual(len(bundle["entry"]), 1)

    def test_snomed_lookup_and_batch(self):
        concept = lookup_snomed_concept("dengue")
        self.assertIsNotNone(concept)
        self.assertEqual(concept["conceptId"], "38362002")

        batch = batch_map_terms(["malaria", "asthma"])
        self.assertEqual(len(batch), 2)
        self.assertIn("61462000", batch["malaria"]["conceptId"])

    def test_snomed_search(self):
        results = search_snomed_concepts("fever")
        self.assertTrue(len(results) >= 2) # high_fever, dengue (fever), typhoid (fever)

if __name__ == "__main__":
    unittest.main()
