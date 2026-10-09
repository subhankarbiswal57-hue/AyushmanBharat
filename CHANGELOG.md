# Changelog

All notable changes to the Ayushman Bharat Digital Health Platform are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/) and adheres to Semantic Versioning.

---

## [2.3.0] - 2026-10-07

### Added
- **C-CDA XML Section & Observation Parser**: Upgraded `services/api_gateway/cda_parser/parser.py` with structured section and vital sign extraction.
- **ABDM Sandbox M1-M3 Milestones**: Implemented verification, care context linking, and consent artefact validation in `services/api_gateway/external_provider_sync/abdm_sync.py`.
- **Clinical Alert Fatigue Reducer**: Added `apps/clinician-frontend/src/alerts/fatigue_reducer.js` with NEWS2 scoring and cooldown deduplication.
- **SMART-on-FHIR EHR Embed Bridge**: Added PostMessage bridge `apps/clinician-frontend/src/ehr-embed/ehr_bridge.js` for zero-context-switching hospital EHR embeds.
- **DPDP Consent Lifecycle Controller**: Added statutory purpose enforcement and immediate revocation in `apps/admin-dashboard/src/consent-management/consent_controller.js`.
- **Accessibility & Low-Literacy Engine**: Added high-contrast mode, scalable typography, and speech synthesis in `apps/patient-frontend/src/accessibility/a11y_helper.js`.
- **Guided Low-Digital-Literacy Onboarding**: Added step-by-step ABHA registration wizard in `apps/patient-frontend/src/onboarding/guided_wizard.js`.
- **WCAG 2.1 AAA Design Tokens**: Created `shared/design-system/tokens.css` with high-contrast palette and 48px minimum touch targets.
- **Clinical Unit Tests**: Created `tests/test_clinical_modules.py` covering C-CDA XML parsing and ABDM sync workflows.

---

## [2.2.0] - 2026-10-06

### Added
- **FHIR R4 Resource Extensions**: Added full `Condition`, `Encounter`, and `Bundle` builders to `services/api_gateway/fhir/mapper.py`.
- **SNOMED CT Clinical Catalog Expansion**: Enriched terminology mappings with communicable (Malaria, Dengue, TB, Typhoid) and chronic conditions, plus keyword search & batch mapping APIs.
- **Audit Ledger Compliance Exports**: Added `/audit/export/json` and `/audit/export/csv` endpoints for statutory DPDP compliance archival and audits.
- **Feature-Level PSI Drift Tracking**: Extended `ai_ml/drift_detection/psi.py` to evaluate drift across physiological vitals (SpO2, heart rate, blood pressure, temperature, age).
- **Token Revocation & Refresh Token Lifecycle**: Added long-lived refresh tokens and an in-memory revocation blacklist to `shared/security.py`.
- **Multilingual i18n Engine**: Added comprehensive English, Hindi, and Odia translation dictionaries and `I18nManager` to `apps/patient-frontend/src/i18n/translations.js`.
- **Offline Storage & Background Sync**: Added IndexedDB queue manager with automated reconnection sync in `apps/patient-frontend/src/offline-fallback/sync_manager.js`.
- **Interoperability Test Suite**: Created `tests/test_fhir_snomed.py` with 6 automated tests covering FHIR mappings and SNOMED searches.
- **HIE & ABDM Architecture Documentation**: Expanded `docs/ARCHITECTURE.md` with ABDM National Digital Health Blueprint specifications.

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

## [2.4.0] - 2026-10-08
### Added
- Added Redis cache environment configuration.
- Added system health constants and ClinicalSeverity type definitions.
- Added StandardErrorResponse schema model.
- Documented REST API versioning guidelines.

- Added VerificationStatus constants.

- Added standard AuditAction enum definitions.

- Added TelemetryCategory enum.
