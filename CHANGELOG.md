# Changelog

All notable changes to the Ayushman Bharat Digital Health Platform are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/) and adheres to Semantic Versioning.

---

## [2.1.0] - 2026-10-05

### Added
- **Structured JSON Logger**: `shared/logger.py` with ISO-8601 timestamps, correlation IDs, and DPDP-compliant PHI data masking.
- **In-Memory TTLCache**: `shared/cache.py` thread-safe LRU cache with hit-rate telemetry for frequent triage assessments.
- **Cryptographic Utility Suite**: `shared/crypto.py` for field-level encryption, deterministic ABHA pseudonymization, and HMAC audit signing.
- **Clinician Triage Modernization**: Redesigned `apps/clinician-frontend/index.html` with Inter typography, dark mode, patient search, and FHIR export.
- **Audit Ledger Query Filters**: Added filtering by `actor_id` and `action` to `services/audit-logging/main.py`.
- **Reusable Pagination**: `shared/pagination.py` models for standardized offset/limit API lists.
- **Validation Test Suite**: `tests/test_validators.py` unit tests with 100% pass rate for domain validators.
- **Progressive Web App Support**: `manifest.json` and service worker `sw.js` for offline clinical workflows.
- **Enhanced Architecture Docs**: Extended `docs/ARCHITECTURE.md` with microservice topologies and DPDP compliance matrix.

---

## [2.0.0] - 2026-10-04

### Added
- Comprehensive README rewrite with architecture diagram and AI/ML pipeline flowchart.
- Unified Governance Console redesign in `apps/admin-dashboard/index.html`.
- Unified `HealthChecker` endpoint in `shared/health.py`.
- Expanded `.gitignore` covering SQLite DBs, environment keys, and ML models.
- Production-pinned `requirements.txt` with security audit compliance.
- Redesigned Beneficiary Patient Portal with dark mode and 12 symptom chips.

---

## [1.1.0] - 2026-10-03
- Added multi-language support for Hindi and Bengali.
- Improved patient onboarding and ABHA registration flow.
