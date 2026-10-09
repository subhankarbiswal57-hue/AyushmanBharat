
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

