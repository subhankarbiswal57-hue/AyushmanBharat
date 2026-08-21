"""
Database Layer - SQLite/SQLAlchemy persistent storage for Ayushman Bharat Platform
Includes Users, Patients, Clinical Encounters, and Cryptographically Hash-Chained Audit Ledger
"""
import sqlite3
import json
import time
import hashlib
import os

DB_PATH = os.environ.get("HEALTH_DB_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "healthtech.db")))

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
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

    # 2. Patients Table
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

    # 3. Encounters Table
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

    # 4. Tamper-Evident Audit Ledger Table (Strict sequential ordering & SHA-256 hash chaining)
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

    # Seed Initial Data if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        seed_data(conn)
    
    conn.close()

def seed_data(conn):
    cursor = conn.cursor()
    now = time.time()

    # Seed Users
    users = [
        ("patient1", hashlib.sha256("patient123".encode()).hexdigest(), "PATIENT", "Aarav Sharma", "14-8899-2341-9988", "rural", "hi", now),
        ("doctor1", hashlib.sha256("doctor123".encode()).hexdigest(), "CLINICIAN", "Dr. Priya Sen", None, "urban", "en", now),
        ("admin1", hashlib.sha256("admin123".encode()).hexdigest(), "ADMIN", "Ayushman Health Administrator", None, "urban", "en", now),
        ("auditor1", hashlib.sha256("auditor123".encode()).hexdigest(), "AUDITOR", "Independent Ethics Auditor", None, "urban", "en", now),
    ]
    cursor.executemany("INSERT OR IGNORE INTO users VALUES (?,?,?,?,?,?,?,?)", users)

    # Seed Patients
    patients = [
        ("P-101", "Aarav Sharma", 42, "male", "rural", "Odisha", "14-8899-2341-9988", "hi", 1, json.dumps(["Hypertension (Borderline)"]), json.dumps(["Penicillin"]), now),
        ("P-102", "Sunita Mohanty", 36, "female", "rural", "Odisha", "14-7711-4422-5533", "od", 1, json.dumps(["Type 2 Diabetes"]), json.dumps(["None"]), now),
        ("P-103", "Rajesh Ghosh", 58, "male", "semi-urban", "West Bengal", "14-3322-1144-8877", "bn", 1, json.dumps(["Asthma"]), json.dumps(["Dust"]), now)
    ]
    cursor.executemany("INSERT OR IGNORE INTO patients VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", patients)

    # Seed Genesis Audit Log
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

if __name__ == "__main__":
    init_database()
    print("[DB] Ayushman Bharat Database initialized successfully at:", DB_PATH)
