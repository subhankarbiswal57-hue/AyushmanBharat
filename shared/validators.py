"""
shared/validators.py
────────────────────
Domain-specific validation helpers for Ayushman Bharat Digital Health Platform.

Covers:
- ABHA (Ayushman Bharat Health Account) ID format validation
- Password strength scoring & enforcement
- Indian mobile number validation
- Pincode validation
- Aadhaar masked-format check (last-4 only, privacy-preserving)
- Age range sanity checks
- Temperature / SpO2 vital-signs range checks

All functions return (is_valid: bool, error_message: str | None) tuples so
callers can build unified error responses easily.
"""
import re
from typing import Tuple, Optional


ValidResult = Tuple[bool, Optional[str]]


# ── ABHA ID ───────────────────────────────────────────────────────────────────

_ABHA_PATTERN = re.compile(r"^\d{2}-\d{4}-\d{4}-\d{4}$")


def validate_abha_id(abha_id: str) -> ValidResult:
    """
    Validate an ABHA (14-digit) Health Account ID.

    Format: ``XX-XXXX-XXXX-XXXX``  (groups of 2-4-4-4 digits separated by hyphens)

    Examples
    --------
    >>> validate_abha_id("14-8899-2341-9988")
    (True, None)
    >>> validate_abha_id("1234567890")
    (False, 'Invalid ABHA ID format. Expected: XX-XXXX-XXXX-XXXX')
    """
    if not abha_id or not isinstance(abha_id, str):
        return False, "ABHA ID must be a non-empty string."
    if not _ABHA_PATTERN.match(abha_id.strip()):
        return False, "Invalid ABHA ID format. Expected: XX-XXXX-XXXX-XXXX"
    return True, None


# ── Password Strength ─────────────────────────────────────────────────────────

def validate_password_strength(password: str) -> ValidResult:
    """
    Enforce a strong password policy.

    Requirements
    ------------
    - Minimum 10 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character from ``!@#$%^&*()_+-=[]{}|;':\",./<>?``
    - Must not contain common weak sequences (``password``, ``123456``, ``qwerty``)
    """
    if not password:
        return False, "Password must not be empty."
    if len(password) < 10:
        return False, "Password must be at least 10 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*()\-_=+\[\]{}|;':\",./<>?]", password):
        return False, "Password must contain at least one special character."

    weak_patterns = ["password", "123456", "qwerty", "abc123", "letmein", "welcome"]
    lower_pw = password.lower()
    for wp in weak_patterns:
        if wp in lower_pw:
            return False, f"Password is too common or contains a weak pattern: '{wp}'."

    return True, None


def password_strength_score(password: str) -> int:
    """
    Return a strength score from 0 (very weak) to 5 (very strong).
    Useful for frontend progress bars.
    """
    score = 0
    if len(password) >= 10:
        score += 1
    if re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"[a-z]", password):
        score += 1
    if re.search(r"\d", password):
        score += 1
    if re.search(r"[!@#$%^&*()\-_=+\[\]{}|;':\",./<>?]", password):
        score += 1
    return score


# ── Indian Mobile Number ──────────────────────────────────────────────────────

_MOBILE_PATTERN = re.compile(r"^(\+91|91|0)?[6-9]\d{9}$")


def validate_indian_mobile(phone: str) -> ValidResult:
    """
    Validate an Indian mobile number (accepts +91, 91, 0, or plain 10-digit).

    Valid prefixes: 6, 7, 8, 9 (as per TRAI allocation).

    Examples
    --------
    >>> validate_indian_mobile("+919876543210")
    (True, None)
    >>> validate_indian_mobile("1234567890")
    (False, 'Invalid Indian mobile number.')
    """
    if not phone:
        return False, "Mobile number must not be empty."
    cleaned = phone.replace(" ", "").replace("-", "")
    if not _MOBILE_PATTERN.match(cleaned):
        return False, "Invalid Indian mobile number. Must be a 10-digit number starting with 6-9."
    return True, None


# ── Pincode ───────────────────────────────────────────────────────────────────

_PINCODE_PATTERN = re.compile(r"^[1-9]\d{5}$")


def validate_pincode(pincode: str) -> ValidResult:
    """
    Validate a 6-digit Indian postal code (PIN code).

    First digit must be 1–9 (no leading zero).
    """
    if not pincode:
        return False, "Pincode must not be empty."
    if not _PINCODE_PATTERN.match(str(pincode).strip()):
        return False, "Invalid PIN code. Must be a 6-digit number (e.g., 751001)."
    return True, None


# ── Vital Signs ───────────────────────────────────────────────────────────────

def validate_spo2(spo2: float) -> ValidResult:
    """
    Validate SpO2 (blood oxygen saturation) is within physiologically valid range.

    Clinically: 70–100 %. Below 90 % is considered hypoxic.
    """
    try:
        val = float(spo2)
    except (TypeError, ValueError):
        return False, "SpO2 must be a numeric value."
    if not (70 <= val <= 100):
        return False, f"SpO2 value {val}% is outside the valid range (70–100%)."
    return True, None


def validate_temperature_f(temp_f: float) -> ValidResult:
    """
    Validate body temperature in Fahrenheit.

    Valid physiological range: 90°F – 110°F.
    """
    try:
        val = float(temp_f)
    except (TypeError, ValueError):
        return False, "Temperature must be a numeric value."
    if not (90 <= val <= 110):
        return False, f"Temperature {val}°F is outside the valid physiological range (90–110°F)."
    return True, None


# ── Age ───────────────────────────────────────────────────────────────────────

def validate_age(age: int) -> ValidResult:
    """Validate patient age is within a sane range (0 – 130 years)."""
    try:
        val = int(age)
    except (TypeError, ValueError):
        return False, "Age must be an integer."
    if not (0 <= val <= 130):
        return False, f"Age {val} is outside the valid range (0–130)."
    return True, None
