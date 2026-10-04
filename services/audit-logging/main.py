"""
Audit Logging Service - FastAPI Application
Cryptographically Hash-Chained, Tamper-Evident Ledger for Governance and Auditing.
Runs on Port 8004
"""
import os
import sys
import json
import time
import hashlib
from typing import Dict, Any, List

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from shared.schemas import AuditEventRequest
from shared.db import get_db_connection, init_database
from shared.config import AUDIT_PORT

init_database()

app = FastAPI(
    title="Ayushman Bharat - Audit Logging Service",
    description="Cryptographically Hash-Chained, Tamper-Evident Ledger",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GENESIS_HASH = "0" * 64

def calculate_hash(record: dict) -> str:
    serialized = f"{record['event_id']}|{record['timestamp']}|{record['action']}|{record['actor_id']}|{record['actor_role']}|{record['target_resource_id']}|{json.dumps(record['details'], sort_keys=True)}|{record['prev_hash']}"
    return hashlib.sha256(serialized.encode()).hexdigest()

def get_latest_audit_hash() -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT record_hash FROM audit_ledger ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row["record_hash"] if row else GENESIS_HASH

def append_audit_event(action: str, actor_id: str, actor_role: str, target_resource_id: str, resource_type: str, details: dict) -> dict:
    prev_hash = get_latest_audit_hash()
    now = time.time()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM audit_ledger")
    count = cursor.fetchone()[0]
    event_id = f"EVT-{int(now*1000)}-{count + 1}"

    record = {
        "event_id": event_id,
        "timestamp": now,
        "action": action,
        "actor_id": actor_id,
        "actor_role": actor_role,
        "target_resource_id": target_resource_id,
        "resource_type": resource_type,
        "details": details,
        "prev_hash": prev_hash
    }
    record["record_hash"] = calculate_hash(record)

    cursor.execute("""
        INSERT INTO audit_ledger (event_id, timestamp, action, actor_id, actor_role, target_resource_id, resource_type, details, prev_hash, record_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record["event_id"],
        record["timestamp"],
        record["action"],
        record["actor_id"],
        record["actor_role"],
        record["target_resource_id"],
        record["resource_type"],
        json.dumps(record["details"], sort_keys=True),
        record["prev_hash"],
        record["record_hash"]
    ))
    conn.commit()
    conn.close()
    return record

def get_audit_records(limit=50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_ledger ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    records = []
    for r in rows:
        d = dict(r)
        d["details"] = json.loads(d.get("details") or "{}")
        records.append(d)
    return records

def verify_audit_ledger_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_ledger ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    is_valid = True
    invalid_indices = []
    prev = GENESIS_HASH
    for i, r in enumerate(rows):
        rec = dict(r)
        rec["details"] = json.loads(rec.get("details") or "{}")
        if rec["prev_hash"] != prev or rec["record_hash"] != calculate_hash(rec):
            is_valid = False
            invalid_indices.append(i)
        prev = rec["record_hash"]

    return {
        "ledger_valid": is_valid,
        "chain_length": len(rows),
        "tampered_records": invalid_indices
    }

@app.get("/health")
def health_check():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM audit_ledger")
    count = cursor.fetchone()[0]
    conn.close()
    return {"service": "audit-logging", "status": "healthy", "chain_length": count}

@app.post("/audit/log", status_code=status.HTTP_201_CREATED)
def record_log(req: AuditEventRequest):
    evt = append_audit_event(
        action=req.action,
        actor_id=req.actor_id,
        actor_role=req.actor_role,
        target_resource_id=req.target_resource_id,
        resource_type=req.resource_type,
        details=req.details
    )
    return {"message": "Audit event recorded", "event": evt}

@app.get("/audit/events")
def list_logs(limit: int = 50, actor_id: str = None, action: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM audit_ledger WHERE 1=1"
    params = []
    if actor_id:
        query += " AND actor_id = ?"
        params.append(actor_id)
    if action:
        query += " AND action = ?"
        params.append(action)
    query += " ORDER BY id DESC LIMIT ?"
    params.append(limit)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Total count
    cursor.execute("SELECT COUNT(*) FROM audit_ledger")
    total_count = cursor.fetchone()[0]
    conn.close()

    events = []
    for r in rows:
        d = dict(r)
        d["details"] = json.loads(d.get("details") or "{}")
        events.append(d)
    return {"events": events, "total": total_count, "returned": len(events)}

@app.get("/audit/verify")
def verify_ledger():
    return verify_audit_ledger_db()

def run_server(port=AUDIT_PORT):
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")

if __name__ == "__main__":
    run_server()
