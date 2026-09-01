"""
Centralized Configuration & Security Settings
Reads from .env or environment variables.
"""
import os
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "ayushman-bharat-secure-production-secret-key-32chars")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./healthtech.db")

LOCKOUT_THRESHOLD = int(os.environ.get("LOCKOUT_THRESHOLD", "5"))
LOCKOUT_DURATION = int(os.environ.get("LOCKOUT_DURATION_SECONDS", "60"))

# Service Endpoints
GATEWAY_PORT = int(os.environ.get("GATEWAY_PORT", "8000"))
AUTH_PORT = int(os.environ.get("AUTH_SERVICE_PORT", "8001"))
CORE_PORT = int(os.environ.get("CORE_SERVICE_PORT", "8002"))
AIML_PORT = int(os.environ.get("AIML_SERVICE_PORT", "8003"))
AUDIT_PORT = int(os.environ.get("AUDIT_SERVICE_PORT", "8004"))
PORTAL_PORT = int(os.environ.get("PORTAL_PORT", "3000"))
