"""
Shared Schemas & Data Models for Ayushman Bharat Healthtech Platform
Includes lightweight FHIR R4 approximations, User Roles, and Audit Events.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
import time

class UserRole:
    PATIENT = "PATIENT"
    CLINICIAN = "CLINICIAN"
    ADMIN = "ADMIN"
    AUDITOR = "AUDITOR"

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
