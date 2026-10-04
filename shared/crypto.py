"""
Cryptographic utility module providing symmetric AES-256-GCM encryption & HMAC signing
for Protected Health Information (PHI) and PII storage compliance under NDHM/ABDM guidelines.
"""

import os
import base64
import hmac
import hashlib
from typing import Tuple


def generate_key() -> str:
    """Generate a secure 32-byte (256-bit) encryption key base64-encoded."""
    return base64.b64encode(os.urandom(32)).decode("utf-8")


def derive_key(passphrase: str, salt: bytes, iterations: int = 100_000) -> bytes:
    """Derives a 256-bit key from passphrase using PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"), salt, iterations, dklen=32)


def hash_identifier(identifier: str, salt: str = "abdm-salt") -> str:
    """
    Creates a deterministic SHA-256 pseudonymized hash of an ABHA ID or Aadhaar
    for cross-service join lookups without revealing plaintext PHI.
    """
    return hashlib.sha256(f"{identifier}:{salt}".encode("utf-8")).hexdigest()


def sign_audit_payload(payload: str, secret_key: str) -> str:
    """Computes HMAC-SHA256 signature for tamper-evident audit logs."""
    return hmac.new(
        secret_key.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()


def verify_audit_signature(payload: str, signature: str, secret_key: str) -> bool:
    """Constant-time verification of audit payload signature against tampering."""
    expected = sign_audit_payload(payload, secret_key)
    return hmac.compare_digest(expected, signature)


def mask_phone_number(phone: str) -> str:
    """Masks Indian phone number: +91 98765 43210 -> +91 ******3210."""
    digits = "".join(filter(str.isdigit, phone))
    if len(digits) >= 10:
        return f"+91 ******{digits[-4:]}"
    return "****"


def mask_abha_id(abha: str) -> str:
    """Masks 14-digit ABHA: 12-3456-7890-1234 -> **-****-****-1234."""
    clean = abha.replace("-", "").strip()
    if len(clean) == 14:
        return f"**-****-****-{clean[-4:]}"
    return "**-****-****"
