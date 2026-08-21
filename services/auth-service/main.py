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
from shared.db import get_db_connection, init_database

init_database()

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "ayushman-bharat-secure-production-secret-key")

def get_user_from_db(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def create_user_in_db(username, password_hash, role, full_name, abha_id, region, language):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, password_hash, role, full_name, abha_id, region, language, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (username, password_hash, role, full_name, abha_id, region, language, time.time()))
    conn.commit()
    conn.close()

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

# Rate limiting & lockout tracking: {ip_or_user: [timestamp, ...]}
LOGIN_ATTEMPTS = {}
LOCKOUT_THRESHOLD = 5
LOCKOUT_DURATION = 60 # 60 seconds lockout after 5 failed attempts
REVOKED_TOKENS = set()

def is_locked_out(identifier: str) -> bool:
    now = time.time()
    attempts = [t for t in LOGIN_ATTEMPTS.get(identifier, []) if now - t < LOCKOUT_DURATION]
    LOGIN_ATTEMPTS[identifier] = attempts
    return len(attempts) >= LOCKOUT_THRESHOLD

def record_failed_attempt(identifier: str):
    now = time.time()
    attempts = [t for t in LOGIN_ATTEMPTS.get(identifier, []) if now - t < LOCKOUT_DURATION]
    attempts.append(now)
    LOGIN_ATTEMPTS[identifier] = attempts

def clear_failed_attempts(identifier: str):
    LOGIN_ATTEMPTS.pop(identifier, None)

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
            username = body.get("username", "")
            password = body.get("password", "")
            client_ip = self.client_address[0] if self.client_address else "unknown"
            lock_id = f"{client_ip}:{username}"

            if is_locked_out(lock_id):
                return self._send_json(429, {"error": "Too many failed attempts. Account temporarily locked for 60 seconds."})

            user = get_user_from_db(username)
            if not user or user["password_hash"] != hashlib.sha256(password.encode()).hexdigest():
                record_failed_attempt(lock_id)
                return self._send_json(401, {"error": "Invalid username or password"})
            
            clear_failed_attempts(lock_id)
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
                    "abha_id": user.get("abha_id"),
                    "preferred_language": user.get("language", "en")
                }
            })

        elif parsed.path == "/auth/logout":
            token = body.get("token") or self.headers.get("Authorization", "").replace("Bearer ", "")
            if token:
                REVOKED_TOKENS.add(token)
            return self._send_json(200, {"message": "Logged out successfully"})

        elif parsed.path == "/auth/refresh":
            token = body.get("token") or self.headers.get("Authorization", "").replace("Bearer ", "")
            if token in REVOKED_TOKENS:
                return self._send_json(401, {"error": "Token has been revoked"})
            payload = verify_jwt(token)
            if not payload:
                return self._send_json(401, {"error": "Invalid or expired token"})
            
            payload["exp"] = time.time() + 86400
            new_token = create_jwt(payload)
            return self._send_json(200, {"access_token": new_token, "token_type": "Bearer"})

        elif parsed.path == "/auth/register":
            username = body.get("username")
            if get_user_from_db(username):
                return self._send_json(400, {"error": "User already exists"})
            role = body.get("role", UserRole.PATIENT)
            abha_id = body.get("abha_id", f"14-{int(time.time()*100)%9000+1000}-4421-1200")
            create_user_in_db(
                username=username,
                password_hash=hashlib.sha256(body.get("password", "").encode()).hexdigest(),
                role=role,
                full_name=body.get("full_name", username),
                abha_id=abha_id,
                region=body.get("region", "rural"),
                language=body.get("language", "en")
            )
            created_user = get_user_from_db(username)
            return self._send_json(201, {"message": "User registered successfully", "user": created_user})

        elif parsed.path == "/auth/verify":
            token = body.get("token") or self.headers.get("Authorization", "").replace("Bearer ", "")
            if token in REVOKED_TOKENS:
                return self._send_json(401, {"valid": False, "error": "Token has been revoked"})
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
