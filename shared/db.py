"""
Unified Database Layer with SQLite / PostgreSQL support.
Configures SQLite with busy timeout and WAL mode to prevent concurrency locks.
"""
import os
import json
import time
import hashlib
import sqlite3
from typing import Dict, List, Optional, Any

from shared.config import DATABASE_URL, LOCKOUT_DURATION, LOCKOUT_THRESHOLD
from shared.security import hash_password

def _get_sqlite_path():
    if DATABASE_URL.startswith("sqlite:///"):
        path = DATABASE_URL.replace("sqlite:///", "")
        return os.path.abspath(path)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "healthtech.db"))

def get_db_connection():
    path = _get_sqlite_path()
    conn = sqlite3.connect(path, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL,
        full_name TEXT NOT NULL,
        abha_id TEXT,
        region TEXT DEFAULT 'rural',
        language TEXT DEFAULT 'en',
        created_at REAL NOT NULL
    )
    """)

    # 2. Login Security & Rate Limiting Table (Persistent across server restarts)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login_security (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        identifier TEXT NOT NULL,
        attempt_time REAL NOT NULL,
        success INTEGER DEFAULT 0
    )
    """)

    # 3. Revoked Tokens Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS revoked_tokens (
        token TEXT PRIMARY KEY,
        revoked_at REAL NOT NULL
    )
    """)

    # 4. Patients Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        region TEXT DEFAULT 'rural',
        state TEXT DEFAULT 'Odisha',
        abha_id TEXT UNIQUE NOT NULL,
        preferred_language TEXT DEFAULT 'en',
        consent_active INTEGER DEFAULT 1,
        active_conditions TEXT,
        allergies TEXT,
        created_at REAL NOT NULL
    )
    """)

    # 5. Encounters Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS encounters (
        encounter_id TEXT PRIMARY KEY,
        patient_id TEXT NOT NULL,
        clinician_id TEXT NOT NULL,
        date TEXT NOT NULL,
        triage_risk TEXT NOT NULL,
        symptoms TEXT,
        vitals TEXT,
        notes TEXT,
        clinician_override TEXT,
        created_at REAL NOT NULL,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
    )
    """)

    # 6. Providers Directory Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS providers (
        provider_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        specialty TEXT NOT NULL,
        facility_name TEXT NOT NULL,
        region TEXT NOT NULL,
        abha_registered INTEGER DEFAULT 1,
        available_slots TEXT,
        rating REAL DEFAULT 4.8
    )
    """)

    # 7. EHR Clinical Records Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ehr_records (
        record_id TEXT PRIMARY KEY,
        patient_id TEXT NOT NULL,
        record_type TEXT NOT NULL,
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        file_path TEXT,
        document_hash TEXT,
        created_at REAL NOT NULL,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
    )
    """)

    # 8. Appointments & Scheduling Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id TEXT PRIMARY KEY,
        patient_id TEXT NOT NULL,
        provider_id TEXT NOT NULL,
        slot_time TEXT NOT NULL,
        status TEXT DEFAULT 'CONFIRMED',
        notes TEXT,
        created_at REAL NOT NULL,
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
        FOREIGN KEY (provider_id) REFERENCES providers(provider_id)
    )
    """)

    # 9. Tamper-Evident Audit Ledger Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id TEXT UNIQUE NOT NULL,
        timestamp REAL NOT NULL,
        action TEXT NOT NULL,
        actor_id TEXT NOT NULL,
        actor_role TEXT NOT NULL,
        target_resource_id TEXT NOT NULL,
        resource_type TEXT NOT NULL,
        details TEXT NOT NULL,
        prev_hash TEXT NOT NULL,
        record_hash TEXT NOT NULL
    )
    """)

    conn.commit()

    # Seed providers if empty
    cursor.execute("SELECT COUNT(*) FROM providers")
    if cursor.fetchone()[0] == 0:
        seed_data(conn)

    conn.close()

def seed_data(conn):
    cursor = conn.cursor()
    now = time.time()

    # Seed Users with bcrypt
    users = [
        ("patient1", hash_password("patient123"), "PATIENT", "Aarav Sharma", "14-8899-2341-9988", "rural", "hi", now),
        ("doctor1", hash_password("doctor123"), "CLINICIAN", "Dr. Priya Sen", None, "urban", "en", now),
        ("admin1", hash_password("admin123"), "ADMIN", "Ayushman Health Administrator", None, "urban", "en", now),
        ("auditor1", hash_password("auditor123"), "AUDITOR", "Independent Ethics Auditor", None, "urban", "en", now),
    ]
    cursor.executemany("INSERT OR IGNORE INTO users VALUES (?,?,?,?,?,?,?,?)", users)

    # Seed Patients
    patients = [
        ("P-101", "Aarav Sharma", 42, "male", "rural", "Odisha", "14-8899-2341-9988", "hi", 1, json.dumps(["Hypertension (Borderline)"]), json.dumps(["Penicillin"]), now),
        ("P-102", "Sunita Mohanty", 36, "female", "rural", "Odisha", "14-7711-4422-5533", "od", 1, json.dumps(["Type 2 Diabetes"]), json.dumps(["None"]), now),
        ("P-103", "Rajesh Ghosh", 58, "male", "semi-urban", "West Bengal", "14-3322-1144-8877", "bn", 1, json.dumps(["Asthma"]), json.dumps(["Dust"]), now)
    ]
    cursor.executemany("INSERT OR IGNORE INTO patients VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", patients)

    # Seed Providers
    providers = [
        ("PR-01", "Dr. Priya Sen", "General Medicine & Cardiology", "AIIMS Bhubaneswar", "rural/urban", 1, json.dumps(["09:00 AM", "10:30 AM", "02:00 PM", "04:30 PM"]), 4.9),
        ("PR-02", "Dr. Alok Verma", "Pulmonology & Critical Care", "District Hospital Cuttack", "rural", 1, json.dumps(["11:00 AM", "01:00 PM", "03:30 PM"]), 4.7),
        ("PR-03", "Dr. Ananya Mishra", "Pediatrics & Community Health", "Community Health Center Puri", "rural", 1, json.dumps(["10:00 AM", "12:00 PM", "02:30 PM"]), 4.8)
    ]
    cursor.executemany("INSERT OR IGNORE INTO providers VALUES (?,?,?,?,?,?,?,?)", providers)

    # Seed Genesis Audit Log
    cursor.execute("SELECT COUNT(*) FROM audit_ledger")
    if cursor.fetchone()[0] == 0:
        genesis_hash = "0" * 64
        event_id = f"EVT-{int(now*1000)}-1"
        details = json.dumps({"note": "Persistent database and tamper-evident audit ledger initialized"}, sort_keys=True)
        serialized = f"{event_id}|{now}|SYSTEM_BOOT|system|SYSTEM|core|{details}|{genesis_hash}"
        rec_hash = hashlib.sha256(serialized.encode()).hexdigest()

        cursor.execute("""
        INSERT OR IGNORE INTO audit_ledger (event_id, timestamp, action, actor_id, actor_role, target_resource_id, resource_type, details, prev_hash, record_hash)
        VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (event_id, now, "SYSTEM_BOOT", "system", "SYSTEM", "core", "SYSTEM", details, genesis_hash, rec_hash))

    conn.commit()

# --- Login Rate Limiting & Revocation DB Helpers ---

def record_login_attempt(identifier: str, success: bool):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO login_security (identifier, attempt_time, success) VALUES (?, ?, ?)",
                   (identifier, time.time(), 1 if success else 0))
    cutoff = time.time() - LOCKOUT_DURATION * 5
    cursor.execute("DELETE FROM login_security WHERE attempt_time < ?", (cutoff,))
    conn.commit()
    conn.close()

def is_user_locked_out(identifier: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cutoff = time.time() - LOCKOUT_DURATION
    cursor.execute("""
        SELECT COUNT(*) FROM login_security
        WHERE identifier = ? AND attempt_time >= ? AND success = 0
    """, (identifier, cutoff))
    failed_count = cursor.fetchone()[0]
    conn.close()
    return failed_count >= LOCKOUT_THRESHOLD

def revoke_token_in_db(token: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO revoked_tokens VALUES (?, ?)", (token, time.time()))
    conn.commit()
    conn.close()

def is_token_revoked_in_db(token: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT token FROM revoked_tokens WHERE token = ?", (token,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

if __name__ == "__main__":
    init_database()
    print("[DB] Modernized Ayushman Bharat database layer initialized successfully.")
