"""
Providers Domain Module
Clinician & Hospital Directory, ABHA Credentialing, and Slot Availability.
"""
import json
from typing import List, Dict, Optional, Any
from shared.db import get_db_connection

def get_all_providers_list() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM providers")
    rows = cursor.fetchall()
    conn.close()
    providers = []
    for r in rows:
        d = dict(r)
        d["available_slots"] = json.loads(d.get("available_slots") or "[]")
        d["abha_registered"] = bool(d.get("abha_registered", 1))
        providers.append(d)
    return providers

def get_provider_by_id(provider_id: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM providers WHERE provider_id = ?", (provider_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        d = dict(row)
        d["available_slots"] = json.loads(d.get("available_slots") or "[]")
        d["abha_registered"] = bool(d.get("abha_registered", 1))
        return d
    return None
