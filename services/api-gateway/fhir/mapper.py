"""
FHIR R4 Resource Mapping Module
Transforms internal patient, encounter, and observation models into standard FHIR R4 JSON resources.
"""
import time
from typing import Dict, Any, List

def to_fhir_patient(patient: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "resourceType": "Patient",
        "id": patient.get("patient_id"),
        "identifier": [
            {
                "system": "https://abdm.gov.in/abha",
                "value": patient.get("abha_id")
            }
        ],
        "active": bool(patient.get("consent_active", True)),
        "name": [
            {
                "use": "official",
                "text": patient.get("name")
            }
        ],
        "gender": patient.get("gender", "unknown"),
        "address": [
            {
                "state": patient.get("state", "Odisha"),
                "type": patient.get("region", "rural")
            }
        ],
        "communication": [
            {
                "language": {
                    "coding": [
                        {
                            "system": "urn:ietf:bcp:47",
                            "code": patient.get("preferred_language", "en")
                        }
                    ]
                }
            }
        ]
    }

def to_fhir_observation(code: str, display: str, value: Any, unit: str, patient_id: str) -> Dict[str, Any]:
    return {
        "resourceType": "Observation",
        "status": "final",
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": code,
                    "display": display
                }
            ]
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valueQuantity": {
            "value": value,
            "unit": unit
        }
    }
