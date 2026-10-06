"""
SNOMED CT Terminology Mapping Module
Standardized mapping between clinical symptoms, diagnosis codes, and SNOMED CT Concept IDs.
"""
from typing import Dict, Optional, Any

SNOMED_DICT = {
    # Emergency & Acute Findings
    "chest_pain": {"conceptId": "29857009", "fsn": "Chest pain (finding)"},
    "shortness_of_breath": {"conceptId": "267036007", "fsn": "Dyspnea (finding)"},
    "high_fever": {"conceptId": "386661006", "fsn": "Fever (finding)"},
    "fainting": {"conceptId": "271594007", "fsn": "Syncope (finding)"},
    "severe_headache": {"conceptId": "25064002", "fsn": "Headache (finding)"},
    "cough": {"conceptId": "49727002", "fsn": "Cough (finding)"},
    "abdominal_pain": {"conceptId": "21522001", "fsn": "Abdominal pain (finding)"},
    "dizziness": {"conceptId": "404640003", "fsn": "Dizziness (finding)"},
    "vomiting": {"conceptId": "422400008", "fsn": "Vomiting (finding)"},
    "fatigue": {"conceptId": "84229001", "fsn": "Fatigue (finding)"},

    # Chronic & Non-Communicable Diseases (NCD)
    "hypertension": {"conceptId": "38341003", "fsn": "Hypertensive disorder (disorder)"},
    "type_2_diabetes": {"conceptId": "44054006", "fsn": "Type 2 diabetes mellitus (disorder)"},
    "type_1_diabetes": {"conceptId": "46635009", "fsn": "Type 1 diabetes mellitus (disorder)"},
    "asthma": {"conceptId": "195967001", "fsn": "Asthma (disorder)"},
    "copd": {"conceptId": "13645005", "fsn": "Chronic obstructive lung disease (disorder)"},
    "chronic_kidney_disease": {"conceptId": "709044004", "fsn": "Chronic kidney disease (disorder)"},
    "coronary_artery_disease": {"conceptId": "53741008", "fsn": "Coronary arteriosclerosis (disorder)"},

    # Communicable Diseases (Endemic & Vector-borne in India)
    "malaria": {"conceptId": "61462000", "fsn": "Malaria (disorder)"},
    "dengue": {"conceptId": "38362002", "fsn": "Dengue fever (disorder)"},
    "tuberculosis": {"conceptId": "56717001", "fsn": "Tuberculosis (disorder)"},
    "typhoid": {"conceptId": "4834000", "fsn": "Typhoid fever (disorder)"},
    "cholera": {"conceptId": "63650001", "fsn": "Cholera (disorder)"},
    "covid_19": {"conceptId": "840539006", "fsn": "COVID-19 (disorder)"}
}

def lookup_snomed_concept(term: str) -> Optional[Dict[str, str]]:
    """Look up a clinical term in the SNOMED dictionary."""
    if not term:
        return None
    key = term.lower().strip().replace(" ", "_").replace("-", "_")
    return SNOMED_DICT.get(key)

def search_snomed_concepts(query: str) -> Dict[str, Dict[str, str]]:
    """Search for SNOMED concepts matching any part of the term or FSN."""
    if not query:
        return {}
    q = query.lower().strip()
    return {
        key: val for key, val in SNOMED_DICT.items()
        if q in key or q in val["fsn"].lower()
    }

def batch_map_terms(terms: list) -> Dict[str, Optional[Dict[str, str]]]:
    """Batch map an array of clinical terms to their SNOMED concepts."""
    return {term: lookup_snomed_concept(term) for term in terms}

