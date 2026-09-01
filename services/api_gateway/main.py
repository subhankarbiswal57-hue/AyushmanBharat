"""
API Gateway & Reverse Proxy - FastAPI Application
Central Entry Point for Web Frontends and Interoperability Clients.
Routes async requests to Auth (8001), Core Backend (8002), AI/ML (8003), and Audit (8004).
Includes FHIR conversion, SNOMED lookups, C-CDA ingestion, and ABDM sync endpoints.
Runs on Port 8000
"""
import os
import sys
import json
import httpx
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, Response, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from shared.config import (
    GATEWAY_PORT, AUTH_PORT, CORE_PORT, AIML_PORT, AUDIT_PORT
)
from shared.security import decode_jwt_token
from services.api_gateway.fhir.mapper import to_fhir_patient, to_fhir_observation
from services.api_gateway.snomed_mapping.lookup import lookup_snomed_concept
from services.api_gateway.cda_parser.parser import parse_ccda_xml
from services.api_gateway.external_provider_sync.abdm_sync import sync_abha_record_to_sandbox

app = FastAPI(
    title="Ayushman Bharat - Central API Gateway",
    description="Unified API Gateway, Reverse Proxy & ABDM/FHIR Interoperability Layer",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICE_ROUTES = {
    "/api/v1/auth": f"http://localhost:{AUTH_PORT}/auth",
    "/api/v1/clinical": f"http://localhost:{CORE_PORT}/clinical",
    "/api/v1/ai": f"http://localhost:{AIML_PORT}/ai",
    "/api/v1/audit": f"http://localhost:{AUDIT_PORT}/audit"
}

@app.get("/health")
def health_check():
    return {
        "gateway": "healthy",
        "version": "2.0.0",
        "routed_services": list(SERVICE_ROUTES.keys()),
        "interoperability": ["FHIR_R4", "SNOMED_CT", "C_CDA_XML", "ABDM_SANDBOX"]
    }

# --- Interoperability Endpoints ---

@app.get("/api/v1/interop/snomed/{term}")
def snomed_lookup(term: str):
    concept = lookup_snomed_concept(term)
    if not concept:
        return {"term": term, "found": False, "message": "No direct mapping found in local SNOMED subset"}
    return {"term": term, "found": True, "concept": concept}

@app.post("/api/v1/interop/cda-parse")
async def parse_cda(request: Request):
    content = await request.body()
    return parse_ccda_xml(content.decode("utf-8", errors="ignore"))

@app.post("/api/v1/interop/abdm-sync")
def sync_abdm(payload: Dict[str, Any]):
    abha_id = payload.get("abha_id", "14-8899-2341-9988")
    return sync_abha_record_to_sandbox(abha_id, payload)

# --- Reverse Proxy Dispatcher ---

@app.api_route("/api/v1/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def reverse_proxy(service: str, path: str, request: Request):
    matched_prefix = f"/api/v1/{service}"
    if matched_prefix not in SERVICE_ROUTES:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not recognized")

    target_base = SERVICE_ROUTES[matched_prefix]
    target_url = f"{target_base}/{path}"
    if request.url.query:
        target_url += f"?{request.url.query}"

    # Gateway Auth Verification
    auth_header = request.headers.get("authorization")
    public_endpoints = ["auth/login", "auth/register", "ai/triage", "ai/fairness-metrics"]
    is_public = any(path.startswith(pe) or f"{service}/{path}".startswith(pe) for pe in public_endpoints)

    if not is_public and auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        claims = decode_jwt_token(token)
        if not claims:
            raise HTTPException(status_code=401, detail="Invalid or expired JWT token at Gateway")
        role = claims.get("role")
        if service == "audit" and role not in ["ADMIN", "AUDITOR"]:
            raise HTTPException(status_code=403, detail=f"Forbidden: Role '{role}' cannot access Audit/Governance")

    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("content-length", None)

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers,
                timeout=10.0
            )
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=dict(resp.headers),
                media_type=resp.headers.get("content-type")
            )
        except httpx.RequestError as e:
            return JSONResponse(
                status_code=502,
                content={"error": f"Bad Gateway connecting to service: {str(e)}", "target": target_url}
            )

def run_server(port=GATEWAY_PORT):
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="warning")

if __name__ == "__main__":
    run_server()
