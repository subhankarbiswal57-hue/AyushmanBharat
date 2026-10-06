"""
C-CDA (Continuity of Care Document) XML Parser
Extracts patient demographics, vital signs, problems, and medication sections from external clinical documents.
"""
import xml.etree.ElementTree as ET
from typing import Dict, Any, List

def parse_ccda_xml(xml_content: str) -> Dict[str, Any]:
    """
    Parses a C-CDA XML document and extracts clinical sections:
    Demographics, Allergies, Vitals, and Medications.
    """
    if not xml_content or not xml_content.strip():
        return {
            "status": "EMPTY_PAYLOAD",
            "document_type": "C-CDA R2.1",
            "sections": {},
            "vitals": [],
            "medications": []
        }

    try:
        # Strip or handle default HL7 XML namespaces for robust xpath querying
        clean_xml = xml_content.strip()
        root = ET.fromstring(clean_xml)

        # Detect namespaces
        ns = {"hl7": "urn:hl7-org:v3"} if "urn:hl7-org:v3" in clean_xml else {}

        # Document Title
        title_elem = root.find(".//hl7:title", ns) if ns else root.find(".//title")
        title = title_elem.text if title_elem is not None and title_elem.text else "Continuity of Care Document"

        # Extract structured sections
        extracted_sections = {}
        section_elems = root.findall(".//hl7:section", ns) if ns else root.findall(".//section")
        for sec in section_elems:
            sec_title = sec.findtext("hl7:title", "", ns) if ns else sec.findtext("title", "")
            sec_text = sec.findtext("hl7:text", "", ns) if ns else sec.findtext("text", "")
            if sec_title:
                extracted_sections[sec_title.strip().lower()] = sec_text.strip()

        # Extract vital signs observations if present
        vitals = []
        obs_nodes = root.findall(".//hl7:observation", ns) if ns else root.findall(".//observation")
        for obs in obs_nodes:
            code_elem = obs.find("hl7:code", ns) if ns else obs.find("code")
            val_elem = obs.find("hl7:value", ns) if ns else obs.find("value")
            if code_elem is not None:
                vitals.append({
                    "code": code_elem.get("code", "unknown"),
                    "display": code_elem.get("displayName", ""),
                    "value": val_elem.get("value", "") if val_elem is not None else "",
                    "unit": val_elem.get("unit", "") if val_elem is not None else ""
                })

        return {
            "status": "PARSED_SUCCESS",
            "document_type": "C-CDA R2.1",
            "title": title,
            "sections_extracted": list(extracted_sections.keys()),
            "sections": extracted_sections,
            "vitals_found": vitals,
            "raw_length": len(xml_content)
        }
    except Exception as e:
        return {
            "status": "PARSED_FALLBACK",
            "document_type": "C-CDA R2.1",
            "title": "Clinical Document (Parsed with Fallback)",
            "error_detail": str(e),
            "raw_length": len(xml_content)
        }

