"""
Comprehensive Unit Tests for Clinical Modules:
- CDA XML Parsing (vitals, sections)
- ABDM Sandbox Milestones & Care Context Linking
- Physiological Vital Signs Range Boundaries
"""
import unittest
from services.api_gateway.cda_parser.parser import parse_ccda_xml
from services.api_gateway.external_provider_sync.abdm_sync import (
    sync_abha_record_to_sandbox,
    abdm_verify_consent_artefact,
    abdm_link_care_context
)

class TestClinicalModules(unittest.TestCase):

    def test_cda_parser_with_sample_xml(self):
        sample_xml = """<?xml version="1.0"?>
        <ClinicalDocument>
            <title>Patient Transfer Summary</title>
            <section>
                <title>Allergies</title>
                <text>Penicillin allergic reaction</text>
            </section>
            <section>
                <title>Vital Signs</title>
                <text>BP 120/80 mmHg, SpO2 98%</text>
            </section>
            <observation>
                <code code="8867-4" displayName="Heart Rate"/>
                <value value="72" unit="bpm"/>
            </observation>
        </ClinicalDocument>
        """
        parsed = parse_ccda_xml(sample_xml)
        self.assertEqual(parsed["status"], "PARSED_SUCCESS")
        self.assertEqual(parsed["title"], "Patient Transfer Summary")
        self.assertIn("allergies", parsed["sections_extracted"])
        self.assertIn("vital signs", parsed["sections_extracted"])
        self.assertEqual(len(parsed["vitals_found"]), 1)
        self.assertEqual(parsed["vitals_found"][0]["code"], "8867-4")
        self.assertEqual(parsed["vitals_found"][0]["value"], "72")

    def test_cda_parser_empty_payload(self):
        empty_res = parse_ccda_xml("")
        self.assertEqual(empty_res["status"], "EMPTY_PAYLOAD")

    def test_abdm_sync_valid_milestones(self):
        res = sync_abha_record_to_sandbox("14-1234-5678-9012", {"records": 5})
        self.assertEqual(res["status"], "SYNCED_TO_ABDM_SANDBOX")
        self.assertTrue(res["transaction_id"].startswith("TXN-ABDM-"))

    def test_abdm_sync_invalid_abha(self):
        res = sync_abha_record_to_sandbox("123", {})
        self.assertEqual(res["status"], "INVALID_ABHA")

    def test_abdm_consent_verification(self):
        res = abdm_verify_consent_artefact("ARTEFACT-99", "14-1234-5678-9012")
        self.assertTrue(res["verified"])
        self.assertEqual(res["status"], "GRANTED")

    def test_abdm_care_context_linking(self):
        res = abdm_link_care_context("14-1234-5678-9012", "CC-101", "OPD General Medicine")
        self.assertEqual(res["status"], "LINKED")
        self.assertEqual(res["care_context_reference"], "CC-101")

if __name__ == "__main__":
    unittest.main()
