"""
Scheduling & Appointments Domain Module
Slot management, conflict checking, and appointment booking.
"""
import time
from typing import List, Dict, Optional, Any
from shared.db import get_db_connection

def book_appointment(patient_id: str, provider_id: str, slot_time: str, notes: str = "") -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    # Conflict check
    cursor.execute("""
        SELECT * FROM appointments
        WHERE provider_id = ? AND slot_time = ? AND status != 'CANCELLED'
    """, (provider_id, slot_time))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        raise ValueError("Slot already booked. Please choose another time slot.")

    cursor.execute("SELECT COUNT(*) FROM appointments")
    count = cursor.fetchone()[0]
    app_id = f"APT-{300 + count + 1}"
    now = time.time()

    cursor.execute("""
        INSERT INTO appointments (appointment_id, patient_id, provider_id, slot_time, status, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (app_id, patient_id, provider_id, slot_time, "CONFIRMED", notes, now))
    conn.commit()
    conn.close()

    return {
        "appointment_id": app_id,
        "patient_id": patient_id,
        "provider_id": provider_id,
        "slot_time": slot_time,
        "status": "CONFIRMED",
        "notes": notes,
        "created_at": now
    }

def get_patient_appointments(patient_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, p.name as provider_name, p.facility_name, p.specialty
        FROM appointments a
        JOIN providers p ON a.provider_id = p.provider_id
        WHERE a.patient_id = ?
        ORDER BY a.created_at DESC
    """, (patient_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
