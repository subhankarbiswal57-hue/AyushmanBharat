"""
Auth Service - Zero-Trust Authentication, RBAC, and ABHA Consent Verification
Runs on port 8001
"""
import sys
import os
import json
import time
import hmac
import hashlib
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from shared.schemas import UserRole

SECRET_KEY = "ayushman-bharat-secure-production-secret-key"

USERS_DB = {
    "patient1": {
        "username": "patient1",
        "password_hash": hashlib.sha256("patient123".encode()).hexdigest(),
        "role": UserRole.PATIENT,
        "full_name": "Aarav Sharma",
        "abha_id": "14-8899-2341-9988",
        "region": "rural",
        "language": "hi"
    },
    "doctor1": {
        "username": "doctor1",
        "password_hash": hashlib.sha256("doctor123".encode()).hexdigest(),
        "role": UserRole.CLINICIAN,
        "full_name": "Dr. Priya Sen",
        "license_no": "MCI-88349",
        "hospital": "AIIMS Bhubaneswar"
    },
    "admin1": {
        "username": "admin1",
        "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": UserRole.ADMIN,
        "full_name": "Ayushman Health Administrator"
    },
    "auditor1": {
        "username": "auditor1",
        "password_hash": hashlib.sha256("auditor123".encode()).hexdigest(),
        "role": UserRole.AUDITOR,
        "full_name": "Independent Ethics & Bias Auditor"
    }
}

def create_jwt(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    signature = hmac.new(SECRET_KEY.encode(), f"{header_b64}.{payload_b64}".encode(), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def verify_jwt(token: str) -> dict:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts
        expected_sig = hmac.new(SECRET_KEY.encode(), f"{header_b64}.{payload_b64}".encode(), hashlib.sha256).digest()
        actual_sig = base64.urlsafe_b64decode(sig_b64 + "=="[:(4 - len(sig_b64) % 4) % 4])
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        payload_json = base64.urlsafe_b64decode(payload_b64 + "=="[:(4 - len(payload_b64) % 4) % 4]).decode()
        payload = json.loads(payload_json)
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None

class AuthHandler(BaseHTTPRequestHandler):
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

        if parsed.path == "/auth/login":
            username = body.get("username")
            password = body.get("password")
            user = USERS_DB.get(username)
            if not user or user["password_hash"] != hashlib.sha256(password.encode()).hexdigest():
                return self._send_json(401, {"error": "Invalid username or password"})
            
            token_payload = {
                "sub": username,
                "role": user["role"],
                "full_name": user["full_name"],
                "abha_id": user.get("abha_id"),
                "exp": time.time() + 86400
            }
            token = create_jwt(token_payload)
            return self._send_json(200, {
                "access_token": token,
                "token_type": "Bearer",
                "user": {
                    "username": username,
                    "role": user["role"],
                    "full_name": user["full_name"],
                    "abha_id": user.get("abha_id")
                }
            })

        elif parsed.path == "/auth/register":
            username = body.get("username")
            if username in USERS_DB:
                return self._send_json(400, {"error": "User already exists"})
            role = body.get("role", UserRole.PATIENT)
            USERS_DB[username] = {
                "username": username,
                "password_hash": hashlib.sha256(body.get("password", "").encode()).hexdigest(),
                "role": role,
                "full_name": body.get("full_name", username),
                "abha_id": body.get("abha_id", f"14-{int(time.time()*100)%9000+1000}-4421-1200"),
                "region": body.get("region", "rural"),
                "language": body.get("language", "en")
            }
            return self._send_json(201, {"message": "User registered successfully", "user": USERS_DB[username]})

        elif parsed.path == "/auth/verify":
            token = body.get("token") or self.headers.get("Authorization", "").replace("Bearer ", "")
            payload = verify_jwt(token)
            if not payload:
                return self._send_json(401, {"valid": False, "error": "Invalid or expired token"})
            return self._send_json(200, {"valid": True, "claims": payload})

        self._send_json(404, {"error": "Not Found"})

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            return self._send_json(200, {"service": "auth-service", "status": "healthy"})
        self._send_json(404, {"error": "Not Found"})

def run_server(port=8001):
    server = HTTPServer(("0.0.0.0", port), AuthHandler)
    print(f"[Auth Service] Running on http://localhost:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
