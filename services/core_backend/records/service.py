"""
EHR Records Domain Module
Storage, hashing, and retrieval of electronic health records (prescriptions, lab reports, discharge summaries).
"""
import os
import time
import hashlib
from typing import List, Dict, Optional, Any
from shared.db import get_db_connection

RECORDS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "storage", "records"))
os.makedirs(RECORDS_DIR, exist_ok=True)

def create_ehr_record(patient_id: str, record_type: str, title: str, summary: str, content: str = "") -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ehr_records")
    count = cursor.fetchone()[0]
    rec_id = f"REC-{200 + count + 1}"

    doc_hash = hashlib.sha256(f"{patient_id}|{title}|{summary}|{content}".encode()).hexdigest()
    file_path = os.path.join(RECORDS_DIR, f"{rec_id}.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"Record Type: {record_type}\nTitle: {title}\nPatient: {patient_id}\n\nSummary:\n{summary}\n\nDetails:\n{content}")

    now = time.time()
    cursor.execute("""
        INSERT INTO ehr_records (record_id, patient_id, record_type, title, summary, file_path, document_hash, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (rec_id, patient_id, record_type, title, summary, file_path, doc_hash, now))
    conn.commit()
    conn.close()

    return {
        "record_id": rec_id,
        "patient_id": patient_id,
        "record_type": record_type,
        "title": title,
        "summary": summary,
        "document_hash": doc_hash,
        "created_at": now
    }

def get_records_by_patient(patient_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ehr_records WHERE patient_id = ? ORDER BY created_at DESC", (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
