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

def to_fhir_condition(condition_id: str, code: str, display: str, patient_id: str, clinical_status: str = "active") -> Dict[str, Any]:
    """Generates a standard FHIR R4 Condition resource."""
    return {
        "resourceType": "Condition",
        "id": condition_id,
        "clinicalStatus": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": clinical_status
                }
            ]
        },
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": code,
                    "display": display
                }
            ]
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "recordedDate": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

def to_fhir_encounter(encounter_id: str, patient_id: str, status: str = "finished", encounter_class: str = "AMB") -> Dict[str, Any]:
    """Generates a standard FHIR R4 Encounter resource."""
    return {
        "resourceType": "Encounter",
        "id": encounter_id,
        "status": status,
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": encounter_class,
            "display": "ambulatory" if encounter_class == "AMB" else "inpatient"
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "period": {
            "start": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }

def to_fhir_bundle(bundle_id: str, entries: List[Dict[str, Any]], bundle_type: str = "collection") -> Dict[str, Any]:
    """Wraps multiple FHIR resources into a standardized FHIR R4 Bundle."""
    return {
        "resourceType": "Bundle",
        "id": bundle_id,
        "type": bundle_type,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total": len(entries),
        "entry": [{"resource": entry} for entry in entries]
    }

