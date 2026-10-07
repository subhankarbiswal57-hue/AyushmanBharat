"""
Shared Schemas & Data Models for Ayushman Bharat Healthtech Platform
Includes Pydantic models for request/response validation across all microservices,
along with dataclass representations and FHIR R4 mappings.
"""
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict

try:
    from pydantic import BaseModel, Field, ConfigDict
except ImportError:
    # Fallback minimal shim if pydantic is not installed
    class BaseModel:
        def __init__(self, **data):
            for k, v in data.items():
                setattr(self, k, v)
        def model_dump(self):
            return self.__dict__
        def dict(self):
            return self.__dict__
    Field = lambda default=None, **kwargs: default
    ConfigDict = dict

class UserRole:
    PATIENT = "PATIENT"
    CLINICIAN = "CLINICIAN"
    ADMIN = "ADMIN"
    AUDITOR = "AUDITOR"

# --- Pydantic Schemas for FastAPI Endpoints ---

class UserRegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "PATIENT"
    full_name: str
    abha_id: Optional[str] = None
    region: str = "rural"
    language: str = "en"

class UserLoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class PatientCreateRequest(BaseModel):
    name: str
    age: int
    gender: str = "other"
    region: str = "rural"
    state: str = "Odisha"
    abha_id: Optional[str] = None
    preferred_language: str = "en"
    active_conditions: List[str] = []
    allergies: List[str] = []

class EncounterCreateRequest(BaseModel):
    patient_id: str
    clinician_id: str = "doctor1"
    triage_risk: str = "LOW"
    symptoms: List[str] = []
    vitals: Dict[str, Any] = {}
    notes: Optional[str] = ""
    clinician_override: Optional[Dict[str, Any]] = None

class AppointmentBookingRequest(BaseModel):
    patient_id: str
    provider_id: str
    slot_time: str
    notes: Optional[str] = ""

class EHRRecordCreateRequest(BaseModel):
    patient_id: str
    record_type: str # Prescription, LabReport, DischargeSummary
    title: str
    summary: str
    document_content: Optional[str] = ""

class TriagePredictRequest(BaseModel):
    symptoms: List[str]
    vitals: Dict[str, Any] = {}
    demographics: Dict[str, Any] = {"gender": "other", "region": "rural", "age": 35}

class AuditEventRequest(BaseModel):
    action: str
    actor_id: str
    actor_role: str
    target_resource_id: str
    resource_type: str
    details: Dict[str, Any] = {}

# --- Dataclasses for Backward Compatibility ---

@dataclass
class PatientDemographics:
    patient_id: str
    name: str
    age: int
    gender: str          # "male", "female", "other"
    region: str          # "rural", "semi-urban", "urban"
    state: str
    abha_id: str         # e.g., "14-8899-2341-9988"
    preferred_language: str = "en"  # "en", "hi", "od", "bn", "ta"
    consent_active: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatientDemographics":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

@dataclass
class ClinicalObservation:
    code: str
    display: str
    value: Any
    unit: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

@dataclass
class TriageAssessment:
    triage_id: str
    patient_id: str
    symptoms: List[str]
    vitals: Dict[str, Any]
    risk_level: str      # "LOW", "MEDIUM", "HIGH", "EMERGENCY"
    risk_score: float    # 0.0 to 1.0
    recommended_care_path: str
    ai_confidence: float
    fairness_metrics: Dict[str, Any]
    clinician_override: Optional[Dict[str, Any]] = None
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class AuditRecord:
    event_id: str
    timestamp: float
    action: str          # e.g., "AUTH_LOGIN", "DATA_READ", "AI_INFERENCE", "CONSENT_MODIFIED"
    actor_id: str
    actor_role: str
    target_resource_id: str
    resource_type: str
    details: Dict[str, Any]
    prev_hash: str
    record_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class StandardErrorResponse(BaseModel):
    error_code: str
    message: str
    timestamp: float
