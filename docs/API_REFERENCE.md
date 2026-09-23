# API Gateway & Microservices Reference

All external API interactions must pass through the API Gateway on port `8000`.

## Endpoints

### 1. Authentication Service (`:8001`)
- `POST /api/v1/auth/register`: Register new patient or clinician account.
- `POST /api/v1/auth/login`: Authenticate and obtain JWT Bearer token.
- `POST /api/v1/auth/refresh`: Refresh expired session token.

### 2. Core Healthcare Service (`:8002`)
- `GET /api/v1/patients/{patient_id}`: Retrieve demographic and ABHA record.
- `POST /api/v1/records`: Ingest clinical encounter or diagnostic report.
- `GET /api/v1/records/fhir/{id}`: Export encounter in standard FHIR R4 Bundle format.

### 3. AI/ML Risk Scoring (`:8004`)
- `POST /api/v1/ai/triage`: Predict clinical urgency score and chronic disease complications.
- `GET /api/v1/ai/fairness-audit`: Inspect model performance across demographic sub-groups.

### 4. Audit & Governance Service (`:8003`)
- `GET /api/v1/audit/logs`: Query tamper-evident event logs with cryptographic hash chain.
