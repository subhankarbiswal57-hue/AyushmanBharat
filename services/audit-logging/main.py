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

AUDIT_CHAIN = []
GENESIS_HASH = "0" * 64

def calculate_hash(record: dict) -> str:
    serialized = f"{record['event_id']}|{record['timestamp']}|{record['action']}|{record['actor_id']}|{record['actor_role']}|{record['target_resource_id']}|{json.dumps(record['details'], sort_keys=True)}|{record['prev_hash']}"
    return hashlib.sha256(serialized.encode()).hexdigest()

def append_audit_event(action: str, actor_id: str, actor_role: str, target_resource_id: str, resource_type: str, details: dict) -> dict:
    prev_hash = AUDIT_CHAIN[-1]["record_hash"] if AUDIT_CHAIN else GENESIS_HASH
    event_id = f"EVT-{int(time.time()*1000)}-{len(AUDIT_CHAIN)+1}"
    record = {
        "event_id": event_id,
        "timestamp": time.time(),
        "action": action,
        "actor_id": actor_id,
        "actor_role": actor_role,
        "target_resource_id": target_resource_id,
        "resource_type": resource_type,
        "details": details,
        "prev_hash": prev_hash
    }
    record["record_hash"] = calculate_hash(record)
    AUDIT_CHAIN.append(record)
    return record

append_audit_event("SYSTEM_BOOT", "system", "SYSTEM", "core", "SYSTEM", {"note": "Audit log ledger initialized"})
append_audit_event("CONSENT_GRANTED", "patient1", "PATIENT", "14-8899-2341-9988", "ABHA_CONSENT", {"scope": "EHR_READ_WRITE", "validity_days": 365})
append_audit_event("AI_BIAS_AUDIT", "ai-engine", "AI_SERVICE", "triage-v1", "MODEL_AUDIT", {"demographic_parity_ratio": 0.94, "fairness_status": "COMPLIANT"})

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
            is_valid = True
            invalid_indices = []
            for i, record in enumerate(AUDIT_CHAIN):
                expected_prev = AUDIT_CHAIN[i-1]["record_hash"] if i > 0 else GENESIS_HASH
                if record["prev_hash"] != expected_prev or record["record_hash"] != calculate_hash(record):
                    is_valid = False
                    invalid_indices.append(i)
            return self._send_json(200, {
                "ledger_valid": is_valid,
                "chain_length": len(AUDIT_CHAIN),
                "tampered_records": invalid_indices
            })

        self._send_json(404, {"error": "Not Found"})

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            return self._send_json(200, {"service": "audit-logging", "status": "healthy", "chain_length": len(AUDIT_CHAIN)})
        elif parsed.path == "/audit/events":
            return self._send_json(200, {"events": list(reversed(AUDIT_CHAIN[-50:])), "total": len(AUDIT_CHAIN)})
        self._send_json(404, {"error": "Not Found"})

def run_server(port=8004):
    server = HTTPServer(("0.0.0.0", port), AuditHandler)
    print(f"[Audit Logging Service] Running on http://localhost:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
