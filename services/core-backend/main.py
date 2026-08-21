"""
Core Clinical Backend Service
Runs on port 8002
Handles FHIR R4 Patient Resources, Observations, Consultation Queues, and Consent State.
"""
import sys
import os
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))
from shared.schemas import PatientDemographics

# In-memory Clinical DB
PATIENTS_DB = {
    "P-101": {
        "patient_id": "P-101",
        "name": "Aarav Sharma",
        "age": 42,
        "gender": "male",
        "region": "rural",
        "state": "Odisha",
        "abha_id": "14-8899-2341-9988",
        "preferred_language": "hi",
        "consent_active": True,
        "active_conditions": ["Hypertension (Borderline)"],
        "allergies": ["Penicillin"]
    },
    "P-102": {
        "patient_id": "P-102",
        "name": "Sunita Mohanty",
        "age": 36,
        "gender": "female",
        "region": "rural",
        "state": "Odisha",
        "abha_id": "14-7711-4422-5533",
        "preferred_language": "od",
        "consent_active": True,
        "active_conditions": ["Type 2 Diabetes"],
        "allergies": ["None"]
    },
    "P-103": {
        "patient_id": "P-103",
        "name": "Rajesh Ghosh",
        "age": 58,
        "gender": "male",
        "region": "semi-urban",
        "state": "West Bengal",
        "abha_id": "14-3322-1144-8877",
        "preferred_language": "bn",
        "consent_active": True,
        "active_conditions": ["Asthma"],
        "allergies": ["Dust"]
    }
}

CLINICAL_ENCOUNTERS = [
    {
        "encounter_id": "ENC-501",
        "patient_id": "P-101",
        "clinician_id": "doctor1",
        "date": "2026-08-21",
        "triage_risk": "MEDIUM",
        "symptoms": ["mild_fever", "cough"],
        "vitals": {"spo2": 97, "pulse": 78, "temperature": 99.4},
        "notes": "Prescribed hydration, paracetamol 650mg SOS. Scheduled telehealth follow up in 3 days."
    }
]

class CoreBackendHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, data: dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self._send_json(200, {"status": "ok"})

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length).decode() or "{}")

        if parsed.path == "/clinical/patients":
            p_id = f"P-{100 + len(PATIENTS_DB) + 1}"
            patient = {
                "patient_id": p_id,
                "name": body.get("name", "Unknown"),
                "age": body.get("age", 30),
                "gender": body.get("gender", "other"),
                "region": body.get("region", "rural"),
                "state": body.get("state", "India"),
                "abha_id": body.get("abha_id", "14-0000-0000-0000"),
                "preferred_language": body.get("preferred_language", "en"),
                "consent_active": True,
                "active_conditions": body.get("active_conditions", []),
                "allergies": body.get("allergies", [])
            }
            PATIENTS_DB[p_id] = patient
            return self._send_json(201, {"message": "Patient registered", "patient": patient})

        elif parsed.path == "/clinical/consent/toggle":
            patient_id = body.get("patient_id")
            patient = PATIENTS_DB.get(patient_id)
            if not patient:
                return self._send_json(404, {"error": "Patient not found"})
            patient["consent_active"] = not patient.get("consent_active", True)
            return self._send_json(200, {
                "patient_id": patient_id,
                "consent_active": patient["consent_active"],
                "message": f"Consent status changed to {'ACTIVE' if patient['consent_active'] else 'REVOKED'}"
            })

        elif parsed.path == "/clinical/encounters":
            enc_id = f"ENC-{500 + len(CLINICAL_ENCOUNTERS) + 1}"
            enc = {
                "encounter_id": enc_id,
                "patient_id": body.get("patient_id"),
                "clinician_id": body.get("clinician_id", "doctor1"),
                "date": time.strftime("%Y-%m-%d"),
                "triage_risk": body.get("triage_risk", "LOW"),
                "symptoms": body.get("symptoms", []),
                "vitals": body.get("vitals", {}),
                "notes": body.get("notes", ""),
                "clinician_override": body.get("clinician_override")
            }
            CLINICAL_ENCOUNTERS.append(enc)
            return self._send_json(201, {"message": "Encounter saved", "encounter": enc})

        self._send_json(404, {"error": "Not Found"})

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            return self._send_json(200, {"service": "core-backend", "status": "healthy", "patients_count": len(PATIENTS_DB)})
        elif parsed.path == "/clinical/patients":
            return self._send_json(200, {"patients": list(PATIENTS_DB.values())})
        elif parsed.path.startswith("/clinical/patients/"):
            p_id = parsed.path.split("/")[-1]
            patient = PATIENTS_DB.get(p_id)
            if not patient:
                return self._send_json(404, {"error": "Patient not found"})
            return self._send_json(200, {"patient": patient})
        elif parsed.path == "/clinical/encounters":
            return self._send_json(200, {"encounters": list(reversed(CLINICAL_ENCOUNTERS))})
        self._send_json(404, {"error": "Not Found"})

def run_server(port=8002):
    server = HTTPServer(("0.0.0.0", port), CoreBackendHandler)
    print(f"[Core Clinical Backend] Running on http://localhost:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
