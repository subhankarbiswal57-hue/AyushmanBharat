"""
Audit Logging Service - Cryptographically Hash-Chained, Tamper-Evident Ledger
Runs on port 8004
"""
import sys
import os
import json
import time
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from shared.db import get_db_connection, init_database

init_database()

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

def get_audit_records(limit=50):
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

class AuditHandler(BaseHTTPRequestHandler):
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

        if parsed.path == "/audit/log":
            event = append_audit_event(
                action=body.get("action", "UNKNOWN"),
                actor_id=body.get("actor_id", "anonymous"),
                actor_role=body.get("actor_role", "UNKNOWN"),
                target_resource_id=body.get("target_resource_id", "N/A"),
                resource_type=body.get("resource_type", "GENERAL"),
                details=body.get("details", {})
            )
            return self._send_json(201, {"message": "Audit event recorded", "event": event})

        elif parsed.path == "/audit/verify":
            verification = verify_audit_ledger_db()
            return self._send_json(200, verification)

        self._send_json(404, {"error": "Not Found"})

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM audit_ledger")
            count = cursor.fetchone()[0]
            conn.close()
            return self._send_json(200, {"service": "audit-logging", "status": "healthy", "chain_length": count})
        elif parsed.path == "/audit/events":
            records = get_audit_records(limit=50)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM audit_ledger")
            count = cursor.fetchone()[0]
            conn.close()
            return self._send_json(200, {"events": records, "total": count})
        self._send_json(404, {"error": "Not Found"})

def run_server(port=8004):
    server = HTTPServer(("0.0.0.0", port), AuditHandler)
    print(f"[Audit Logging Service] Running on http://localhost:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
