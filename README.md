# 🏥 Ayushman Bharat Digital Health Platform

> **Equity-first, AI-assisted care delivery infrastructure for India's public health system.**  
> Multi-sided platform (patients · clinicians · health systems) treating digital exclusion, privacy/security, algorithmic bias, workflow burden, and interoperability as **first-class architecture concerns** — not afterthoughts.

[![CI/CD Pipeline](https://github.com/subhankarbiswal57-hue/AyushmanBharat/actions/workflows/ci.yml/badge.svg)](https://github.com/subhankarbiswal57-hue/AyushmanBharat/actions)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![ABDM](https://img.shields.io/badge/ABDM-Integrated-blue)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Risk Area → Folder Ownership](#risk-area--folder-ownership)
- [Services](#services)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [AI/ML Pipeline](#aiml-pipeline)
- [Security](#security)
- [Contributing](#contributing)

---

## Overview

The platform addresses five systemic risks in India's digital health ecosystem:

| Risk | Impact | How We Address It |
|------|--------|-------------------|
| **Digital exclusion** | ~600M citizens lack digital literacy | Multilingual UI (6 languages), offline fallback triage, low-bandwidth design |
| **Privacy & security** | Health data is sensitive PII | Zero-trust auth, end-to-end encryption, DPDP Act 2023 compliance |
| **Algorithmic bias** | AI can perpetuate healthcare disparity | Demographic parity monitoring, Four-Fifths rule enforcement, SHAP explainability |
| **Clinician burden** | Alert fatigue reduces care quality | AI triage pre-scoring, EHR embed, clinician override audit trail |
| **Interoperability** | Fragmented records = missed diagnoses | FHIR R4, ABDM Gateway, SNOMED-CT, CDA parsing |

---

## Architecture

```
ayushmanBharat/
├── apps/
│   ├── patient-frontend/       # Equity & access — multilingual, dark mode, offline triage
│   ├── clinician-frontend/     # Workflow burden — EHR embed, AI explanations, alerts
│   ├── admin-dashboard/        # Governance — fairness metrics, audit ledger, consent mgmt
│   └── unified-portal/         # PWA shell — service worker, offline support
│
├── services/
│   ├── api-gateway/            # Interoperability — FHIR R4, ABDM proxy, SNOMED mapping
│   ├── auth-service/           # Privacy & security — JWT, RBAC, brute-force protection
│   ├── core-backend/           # Clinical logic — patients, encounters, scheduling, EHR
│   └── audit-logging/          # Governance — SHA-256 tamper-evident event chain
│
├── ai-ml/ (ai_ml/)             # AI fairness layer
│   ├── models/                 # Triage model training (scikit-learn)
│   ├── evaluation/             # Fairness evaluator — demographic parity, equalized odds
│   ├── explainability/         # SHAP-based explanations for clinicians
│   └── monitoring/             # PSI drift detection, subgroup performance
│
├── shared/                     # Cross-cutting utilities
│   ├── config.py               # Centralized port & env config
│   ├── db.py                   # SQLite connection pool & init
│   ├── schemas.py              # Pydantic models (single source of truth)
│   ├── security.py             # bcrypt + PyJWT helpers
│   ├── rate_limiter.py         # Sliding-window rate limiting (FastAPI dep)
│   ├── validators.py           # ABHA ID, password strength, mobile, vitals
│   └── health.py               # Unified /health + /health/detail endpoints
│
├── infra/                      # Docker Compose, Dockerfiles
├── docs/                       # ABDM integration, security policy, API reference
├── tests/                      # Unit + integration test suite
├── .github/workflows/ci.yml    # 5-job CI: lint, matrix tests, ML, integration, CVE scan
├── requirements.txt            # Pinned dependencies
└── docker-compose.yml          # Full-stack local development
```

---

## Risk Area → Folder Ownership

| Risk Area | Primary Owner | Secondary |
|-----------|--------------|-----------|
| Digital exclusion / equity | `apps/patient-frontend/` | `apps/unified-portal/` |
| Privacy & security | `services/auth-service/` | `shared/security.py`, `shared/rate_limiter.py` |
| AI/algorithmic bias | `ai_ml/evaluation/` | `ai_ml/monitoring/`, `apps/admin-dashboard/` |
| Workflow / clinician burden | `apps/clinician-frontend/` | `services/core-backend/` |
| Interoperability / fragmentation | `services/api-gateway/` | `services/core-backend/` |
| Governance (cross-cutting) | `services/audit-logging/` | `apps/admin-dashboard/`, `docs/governance/` |

---

## Services

### Auth Service (`:8001`)
- **JWT** tokens with role-based access control (`patient`, `clinician`, `admin`)
- **Brute-force protection** — per-IP + per-username sliding-window lockout
- **Token revocation** — blacklist stored in DB for logout/breach response
- **Rate limiting** — 5 auth requests/minute per IP via `shared/rate_limiter.py`

### Core Backend (`:8002`)
- **FHIR R4** patient, encounter, and provider resources
- **EHR records** with full audit trail on every mutation
- **Scheduling** — appointment booking with conflict detection
- **Consent toggle** — real-time ABDM Gateway-synced consent status

### API Gateway (`:8000`)
- Single entry point for all frontends
- **ABDM proxy** — routes authenticated requests to National Health Authority endpoints
- **FHIR mapper** — normalises external records to internal schema
- **SNOMED-CT lookup** — resolves clinical terminology codes

### AI/ML Service (`:8003`)
- **Triage model** — scikit-learn RandomForest trained on synthetic clinical data
- **Fairness evaluation** — demographic parity, equalized odds, disparate impact ratio
- **SHAP explainability** — feature importance per prediction for clinician review
- **PSI drift detection** — alerts when population shift degrades model fairness

### Audit Logging (`:8004`)
- **Tamper-evident event chain** — each record hashed with SHA-256 over previous hash
- Captures: EHR reads/writes, consent changes, AI triage runs, clinician overrides
- Queryable via admin dashboard with live auto-refresh

---

## Quick Start

### Prerequisites
- Python 3.10+ 
- Docker & Docker Compose (optional, for full stack)

### Local Development

```bash
# 1. Clone
git clone https://github.com/subhankarbiswal57-hue/AyushmanBharat.git
cd AyushmanBharat

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Train the ML model
python ai_ml/models/train.py

# 5. Start all services
python run_all.py
```

### Docker (Full Stack)

```bash
docker compose up --build
```

Services will be available at:
| Service | URL |
|---------|-----|
| API Gateway | http://localhost:8000 |
| Auth Service | http://localhost:8001 |
| Core Backend | http://localhost:8002 |
| AI/ML Service | http://localhost:8003 |
| Patient Frontend | `apps/patient-frontend/index.html` |
| Admin Dashboard | `apps/admin-dashboard/index.html` |

---

## API Reference

Full documentation: [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md)

### Key Endpoints

```
POST  /auth/register            Register new user (patient/clinician/admin)
POST  /auth/login               Obtain JWT bearer token
GET   /auth/me                  Get current user profile
POST  /auth/logout              Revoke token

GET   /clinical/patients        List all patients
POST  /clinical/patients        Register new patient (FHIR R4)
POST  /clinical/consent/toggle  Toggle ABDM consent for a patient
POST  /clinical/encounters      Record clinical encounter
POST  /clinical/appointments    Book appointment

POST  /api/v1/ai/triage         Run AI symptom triage
GET   /api/v1/ai/fairness-metrics  Get demographic parity metrics
GET   /api/v1/audit/events      Query tamper-evident audit log

GET   /health                   Liveness probe (all services)
GET   /health/detail            Full health report with component status
```

---

## AI/ML Pipeline

```
Raw Symptoms + Vitals + Demographics
          │
          ▼
  Demographic Parity Guard   ← shared/validators.py validates input ranges
          │
          ▼
  RandomForest Triage Model  ← ai_ml/models/triage_model.joblib
          │
          ▼
  Risk Score + Level         → EMERGENCY / HIGH / MEDIUM / LOW
          │
          ▼
  SHAP Explainability        → Feature importance for clinician UI
          │
          ▼
  Fairness Monitor           → PSI drift alert if distribution shifts
```

**Fairness targets enforced:**
- Demographic Parity Ratio ≥ 0.80 (gender, region, age group)
- Disparate Impact Ratio ≥ 0.80 (Four-Fifths Rule)
- Model re-evaluated every 6 hours against protected attributes

---

## Security

See [`docs/SECURITY.md`](docs/SECURITY.md) for vulnerability reporting.

Key security controls:
- 🔐 **bcrypt** password hashing (cost factor 12)
- 🔑 **JWT** with configurable expiry + server-side revocation
- 🛡️ **Zero-trust** — every request authenticated and RBAC-checked
- 🚦 **Rate limiting** — auth: 5 req/min, AI: 30 req/min, API: 120 req/min
- 🔍 **Bandit** static security analysis in CI
- 📦 **pip-audit** CVE scanning on every PR
- 📋 **SHA-256 audit chain** — cryptographic event integrity

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines.

```bash
# Run tests
pytest tests/ -v --cov=shared --cov=services

# Lint
flake8 services/ shared/ ai_ml/ --max-line-length=100

# Security scan
bandit -r services/ shared/ ai_ml/ -ll
```

---

*Built with ❤️ for Bharat · ABDM Compliant · DPDP Act 2023 · Open Source*
