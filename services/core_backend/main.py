"""
Core Clinical Backend Service - FastAPI Application
Handles FHIR R4 Patients, Encounters, Providers Directory, EHR Storage, and Scheduling.
Runs on Port 8002
"""
import os
import sys
import json
import time
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from shared.schemas import (
    PatientCreateRequest, EncounterCreateRequest,
    AppointmentBookingRequest, EHRRecordCreateRequest
)
from shared.db import get_db_connection, init_database
from shared.config import CORE_PORT

# Domain Services
from services.core_backend.patients.service import (
    get_all_patients_list, get_patient_by_id,
    create_patient_record, toggle_patient_consent_status
)
from services.core_backend.providers.service import (
    get_all_providers_list, get_provider_by_id
)
from services.core_backend.records.service import (
    create_ehr_record, get_records_by_patient
)
from services.core_backend.scheduling.service import (
    book_appointment, get_patient_appointments
)

init_database()

app = FastAPI(
    title="Ayushman Bharat - Core Clinical Backend",
    description="Clinical Record Management, Encounters, Providers & Scheduling",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    patients = get_all_patients_list()
    return {"service": "core-backend", "status": "healthy", "patients_count": len(patients)}

# --- Patients Endpoints ---

@app.get("/clinical/patients")
def list_patients():
    return {"patients": get_all_patients_list()}

@app.get("/clinical/patients/{patient_id}")
def get_patient(patient_id: str):
    patient = get_patient_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return {"patient": patient}

@app.post("/clinical/patients", status_code=status.HTTP_201_CREATED)
def register_patient(req: PatientCreateRequest):
    new_patient = create_patient_record(req.model_dump() if hasattr(req, "model_dump") else req.dict())
    return {"message": "Patient registered successfully", "patient": new_patient}

@app.post("/clinical/consent/toggle")
def toggle_consent(body: Dict[str, str]):
    patient_id = body.get("patient_id")
    if not patient_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="patient_id is required")
    res = toggle_patient_consent_status(patient_id)
    if res is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return {"patient_id": patient_id, "consent_active": res, "message": f"Consent status changed to {'ACTIVE' if res else 'REVOKED'}"}

# --- Encounters Endpoints ---

@app.get("/clinical/encounters")
def list_encounters():
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
    return {"encounters": encounters}

@app.post("/clinical/encounters", status_code=status.HTTP_201_CREATED)
def record_encounter(req: EncounterCreateRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM encounters")
    count = cursor.fetchone()[0]
    enc_id = f"ENC-{500 + count + 1}"
    now = time.time()

    cursor.execute("""
        INSERT INTO encounters (encounter_id, patient_id, clinician_id, date, triage_risk, symptoms, vitals, notes, clinician_override, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        enc_id,
        req.patient_id,
        req.clinician_id,
        time.strftime("%Y-%m-%d"),
        req.triage_risk,
        json.dumps(req.symptoms),
        json.dumps(req.vitals),
        req.notes,
        json.dumps(req.clinician_override) if req.clinician_override else None,
        now
    ))
    conn.commit()
    conn.close()
    return {"message": "Encounter saved successfully", "encounter_id": enc_id}

# --- Providers Endpoints ---

@app.get("/clinical/providers")
def list_providers():
    return {"providers": get_all_providers_list()}

@app.get("/clinical/providers/{provider_id}")
def get_provider(provider_id: str):
    prov = get_provider_by_id(provider_id)
    if not prov:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    return {"provider": prov}

# --- EHR Records Endpoints ---

@app.get("/clinical/records/{patient_id}")
def list_patient_records(patient_id: str):
    records = get_records_by_patient(patient_id)
    return {"patient_id": patient_id, "records": records}

@app.post("/clinical/records", status_code=status.HTTP_201_CREATED)
def create_record(req: EHRRecordCreateRequest):
    rec = create_ehr_record(
        patient_id=req.patient_id,
        record_type=req.record_type,
        title=req.title,
        summary=req.summary,
        content=req.document_content or ""
    )
    return {"message": "EHR record created successfully", "record": rec}

# --- Scheduling Endpoints ---

@app.get("/clinical/appointments/{patient_id}")
def list_appointments(patient_id: str):
    apts = get_patient_appointments(patient_id)
    return {"patient_id": patient_id, "appointments": apts}

@app.post("/clinical/appointments", status_code=status.HTTP_201_CREATED)
def schedule_appointment(req: AppointmentBookingRequest):
    try:
        apt = book_appointment(req.patient_id, req.provider_id, req.slot_time, req.notes or "")
        return {"message": "Appointment scheduled successfully", "appointment": apt}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

def run_server(port=CORE_PORT):
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")

if __name__ == "__main__":
    run_server()
