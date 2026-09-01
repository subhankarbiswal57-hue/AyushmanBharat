"""
Cryptographic Token & Hashing Utilities
Provides real PyJWT creation and verification, along with secure bcrypt password hashing.
Falls back cleanly to hashlib/hmac if bcrypt/jwt libraries are not yet installed.
"""
import time
from typing import Optional, Dict, Any
from shared.config import JWT_SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Password Hashing
try:
    import bcrypt
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
                return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception:
            pass
        # Fallback verification for legacy SHA-256 seed hashes
        import hashlib
        return hashlib.sha256(plain_password.encode("utf-8")).hexdigest() == hashed_password
except ImportError:
    import hashlib
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return hashlib.sha256(password.encode("utf-8")).hexdigest() == hashed_password

# JWT Management
try:
    import jwt
    def create_jwt_token(payload: Dict[str, Any], expires_delta: Optional[float] = None) -> str:
        to_encode = payload.copy()
        now = time.time()
        expire = now + (expires_delta if expires_delta else (ACCESS_TOKEN_EXPIRE_MINUTES * 60))
        to_encode.update({
            "exp": int(expire),
            "iat": int(now),
            "iss": "ayushman-bharat-auth-service"
        })
        return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

    def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(
                token,
                JWT_SECRET_KEY,
                algorithms=[ALGORITHM],
                options={"verify_signature": True, "verify_exp": True}
            )
        except Exception:
            return None
except ImportError:
    import hmac, hashlib, base64, json
    def create_jwt_token(payload: Dict[str, Any], expires_delta: Optional[float] = None) -> str:
        now = time.time()
        expire = now + (expires_delta if expires_delta else (ACCESS_TOKEN_EXPIRE_MINUTES * 60))
        to_encode = payload.copy()
        to_encode.update({"exp": int(expire), "iat": int(now), "iss": "ayushman-bharat-auth-service"})
        header = {"alg": ALGORITHM, "typ": "JWT"}
        h_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
        p_b64 = base64.urlsafe_b64encode(json.dumps(to_encode).encode()).decode().rstrip("=")
        sig = hmac.new(JWT_SECRET_KEY.encode(), f"{h_b64}.{p_b64}".encode(), hashlib.sha256).digest()
        s_b64 = base64.urlsafe_b64encode(sig).decode().rstrip("=")
        return f"{h_b64}.{p_b64}.{s_b64}"

    def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            h_b64, p_b64, s_b64 = parts
            expected_sig = hmac.new(JWT_SECRET_KEY.encode(), f"{h_b64}.{p_b64}".encode(), hashlib.sha256).digest()
            actual_sig = base64.urlsafe_b64decode(s_b64 + "=="[:(4 - len(s_b64) % 4) % 4])
            if not hmac.compare_digest(expected_sig, actual_sig):
                return None
            p_json = base64.urlsafe_b64decode(p_b64 + "=="[:(4 - len(p_b64) % 4) % 4]).decode()
            payload = json.loads(p_json)
            if payload.get("exp", 0) < time.time():
                return None
            return payload
        except Exception:
            return None
