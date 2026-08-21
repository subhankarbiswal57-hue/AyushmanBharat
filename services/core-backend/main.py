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
from shared.db import get_db_connection, init_database

init_database()

def get_all_patients():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients")
    rows = cursor.fetchall()
    conn.close()
    patients = []
    for r in rows:
        d = dict(r)
        d["active_conditions"] = json.loads(d.get("active_conditions") or "[]")
        d["allergies"] = json.loads(d.get("allergies") or "[]")
        d["consent_active"] = bool(d.get("consent_active", 1))
        patients.append(d)
    return patients

def get_patient(patient_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["active_conditions"] = json.loads(d.get("active_conditions") or "[]")
        d["allergies"] = json.loads(d.get("allergies") or "[]")
        d["consent_active"] = bool(d.get("consent_active", 1))
        return d
    return None

def toggle_patient_consent(patient_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT consent_active FROM patients WHERE patient_id = ?", (patient_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    new_state = 0 if row["consent_active"] else 1
    cursor.execute("UPDATE patients SET consent_active = ? WHERE patient_id = ?", (new_state, patient_id))
    conn.commit()
    conn.close()
    return bool(new_state)

def save_encounter_to_db(enc: dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO encounters (encounter_id, patient_id, clinician_id, date, triage_risk, symptoms, vitals, notes, clinician_override, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        enc["encounter_id"],
        enc["patient_id"],
        enc["clinician_id"],
        enc["date"],
        enc["triage_risk"],
        json.dumps(enc.get("symptoms", [])),
        json.dumps(enc.get("vitals", {})),
        enc.get("notes", ""),
        enc.get("clinician_override"),
        time.time()
    ))
    conn.commit()
    conn.close()

def get_all_encounters():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM encounters ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    encounters = []
    for r in rows:
        d = dict(r)
        d["symptoms"] = json.loads(d.get("symptoms") or "[]")
        d["vitals"] = json.loads(d.get("vitals") or "{}")
        encounters.append(d)
    return encounters

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
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM patients")
            count = cursor.fetchone()[0]
            p_id = f"P-{100 + count + 1}"
            patient = {
                "patient_id": p_id,
                "name": body.get("name", "Unknown"),
                "age": body.get("age", 30),
                "gender": body.get("gender", "other"),
                "region": body.get("region", "rural"),
                "state": body.get("state", "India"),
                "abha_id": body.get("abha_id", f"14-{int(time.time()*100)%9000+1000}-0000-0000"),
                "preferred_language": body.get("preferred_language", "en"),
                "consent_active": 1,
                "active_conditions": json.dumps(body.get("active_conditions", [])),
                "allergies": json.dumps(body.get("allergies", [])),
                "created_at": time.time()
            }
            cursor.execute("""
                INSERT INTO patients VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, tuple(patient.values()))
            conn.commit()
            conn.close()
            return self._send_json(201, {"message": "Patient registered", "patient": get_patient(p_id)})

        elif parsed.path == "/clinical/consent/toggle":
            patient_id = body.get("patient_id")
            new_consent = toggle_patient_consent(patient_id)
            if new_consent is None:
                return self._send_json(404, {"error": "Patient not found"})
            return self._send_json(200, {
                "patient_id": patient_id,
                "consent_active": new_consent,
                "message": f"Consent status changed to {'ACTIVE' if new_consent else 'REVOKED'}"
            })

        elif parsed.path == "/clinical/encounters":
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM encounters")
            count = cursor.fetchone()[0]
            conn.close()
            enc_id = f"ENC-{500 + count + 1}"
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
            save_encounter_to_db(enc)
            return self._send_json(201, {"message": "Encounter saved", "encounter": enc})

        self._send_json(404, {"error": "Not Found"})

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            patients = get_all_patients()
            return self._send_json(200, {"service": "core-backend", "status": "healthy", "patients_count": len(patients)})
        elif parsed.path == "/clinical/patients":
            return self._send_json(200, {"patients": get_all_patients()})
        elif parsed.path.startswith("/clinical/patients/"):
            p_id = parsed.path.split("/")[-1]
            patient = get_patient(p_id)
            if not patient:
                return self._send_json(404, {"error": "Patient not found"})
            return self._send_json(200, {"patient": patient})
        elif parsed.path == "/clinical/encounters":
            return self._send_json(200, {"encounters": get_all_encounters()})
        self._send_json(404, {"error": "Not Found"})

def run_server(port=8002):
    server = HTTPServer(("0.0.0.0", port), CoreBackendHandler)
    print(f"[Core Clinical Backend] Running on http://localhost:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
