"""
SNOMED CT Terminology Mapping Module
Standardized mapping between clinical symptoms, diagnosis codes, and SNOMED CT Concept IDs.
"""
from typing import Dict, Optional, Any

SNOMED_DICT = {
    "chest_pain": {"conceptId": "29857009", "fsn": "Chest pain (finding)"},
    "shortness_of_breath": {"conceptId": "267036007", "fsn": "Dyspnea (finding)"},
    "high_fever": {"conceptId": "386661006", "fsn": "Fever (finding)"},
    "fainting": {"conceptId": "271594007", "fsn": "Syncope (finding)"},
    "severe_headache": {"conceptId": "25064002", "fsn": "Headache (finding)"},
    "cough": {"conceptId": "49727002", "fsn": "Cough (finding)"},
    "hypertension": {"conceptId": "38341003", "fsn": "Hypertensive disorder (disorder)"},
    "type_2_diabetes": {"conceptId": "44054006", "fsn": "Type 2 diabetes mellitus (disorder)"},
    "asthma": {"conceptId": "195967001", "fsn": "Asthma (disorder)"}
}

def lookup_snomed_concept(term: str) -> Optional[Dict[str, str]]:
    key = term.lower().strip().replace(" ", "_").replace("-", "_")
    return SNOMED_DICT.get(key)
