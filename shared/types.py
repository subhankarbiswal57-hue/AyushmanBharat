
# Verification status flags
class VerificationStatus:
    PENDING = 'PENDING'
    VERIFIED = 'VERIFIED'
    REJECTED = 'REJECTED'


# Audit action codes
class AuditAction:
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'


# Telemetry event categories
class TelemetryCategory:
    AUTH = 'AUTH'
    TRANSACTION = 'TRANSACTION'
    SECURITY = 'SECURITY'


# Role definitions
class UserRole:
    ADMIN = 'ADMIN'
    OPERATOR = 'OPERATOR'
    AUDITOR = 'AUDITOR'
    CLINICIAN = 'CLINICIAN'
    BENEFICIARY = 'BENEFICIARY'


# Consent Status lifecycles
class ConsentStatus:
    REQUESTED = 'REQUESTED'
    GRANTED = 'GRANTED'
    DENIED = 'DENIED'
    REVOKED = 'REVOKED'
    EXPIRED = 'EXPIRED'

# ABHA Authentication Modes
class ABHAMode:
    MOBILE_OTP = 'MOBILE_OTP'
    AADHAAR_OTP = 'AADHAAR_OTP'
    DEMOGRAPHICS = 'DEMOGRAPHICS'
    PASSWORD = 'PASSWORD'
