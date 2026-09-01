"""
Auth Service - Fast API Application
Zero-Trust Authentication, RBAC, PyJWT tokens, and Persistent Brute-Force Protection.
Runs on Port 8001
"""
import os
import sys
import time
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, Header, Request, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from shared.schemas import UserRegisterRequest, UserLoginRequest, TokenResponse, UserRole
from shared.db import (
    get_db_connection, init_database,
    record_login_attempt, is_user_locked_out,
    revoke_token_in_db, is_token_revoked_in_db
)
from shared.security import hash_password, verify_password, create_jwt_token, decode_jwt_token
from shared.config import AUTH_PORT

init_database()

app = FastAPI(
    title="Ayushman Bharat - Auth Service",
    description="Zero-Trust Authentication, RBAC, and ABHA Security",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_user_from_db(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# Dependency for protected routes
def get_current_user(authorization: str = Header(None)) -> Dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid token")
    token = authorization.split(" ")[1]
    if is_token_revoked_in_db(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
    payload = decode_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return payload

@app.get("/health")
def health_check():
    return {"service": "auth-service", "status": "healthy", "version": "2.0.0"}

@app.post("/auth/register", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
def register(req: UserRegisterRequest):
    existing = get_user_from_db(req.username)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    hashed_pw = hash_password(req.password)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, password_hash, role, full_name, abha_id, region, language, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (req.username, hashed_pw, req.role, req.full_name, req.abha_id, req.region, req.language, time.time()))
    conn.commit()
    conn.close()

    return {"message": "User registered successfully", "username": req.username, "role": req.role}

@app.post("/auth/login", response_model=TokenResponse)
def login(req: UserLoginRequest, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    lockout_key = f"{client_ip}:{req.username}"

    if is_user_locked_out(lockout_key) or is_user_locked_out(req.username):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account temporarily locked due to excessive failed attempts. Please retry in 60s."
        )

    user = get_user_from_db(req.username)
    if not user or not verify_password(req.password, user["password_hash"]):
        record_login_attempt(lockout_key, success=False)
        record_login_attempt(req.username, success=False)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    # Record successful attempt
    record_login_attempt(lockout_key, success=True)
    record_login_attempt(req.username, success=True)

    token_payload = {
        "sub": user["username"],
        "role": user["role"],
        "full_name": user["full_name"],
        "abha_id": user.get("abha_id"),
        "region": user.get("region"),
        "language": user.get("language")
    }
    token = create_jwt_token(token_payload)

    user_info = {
        "username": user["username"],
        "role": user["role"],
        "full_name": user["full_name"],
        "abha_id": user.get("abha_id"),
        "region": user.get("region"),
        "language": user.get("language")
    }

    return TokenResponse(access_token=token, token_type="bearer", user=user_info)

@app.get("/auth/me")
def get_me(user: Dict[str, Any] = Depends(get_current_user)):
    return {"user": user}

@app.post("/auth/logout")
def logout(authorization: str = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        revoke_token_in_db(token)
    return {"message": "Logged out successfully and token revoked"}

# Standalone helper for tests / integration backwards compatibility
create_jwt = create_jwt_token
verify_jwt = decode_jwt_token

def run_server(port=AUTH_PORT):
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")

if __name__ == "__main__":
    run_server()
