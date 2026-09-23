# Ayushman Bharat Architecture & Ecosystem Overview

```mermaid
graph TD
    A[Patient / Beneficiary Mobile App] -->|HTTPS / WSS| G[API Gateway :8000]
    B[Clinician Portal / EMR] -->|HTTPS| G
    C[Admin / Governance Dashboard] -->|HTTPS| G
    G --> D[Auth Service :8001]
    G --> E[Core Healthcare Service :8002]
    G --> F[Audit Logging Service :8003]
    G --> H[AI/ML Risk Engine :8004]
    E --> I[(PostgreSQL / SQLite)]
    F --> J[(Tamper-Proof Audit Store)]
    E --> K[ABDM Gateway Interop Layer]
    K --> L[National Health Authority ABDM Switch]
```

## Architectural Pillars
- **Zero-Trust & Consent-Driven**: Every patient record query requires a cryptographically validated ABDM consent artifact.
- **Fairness & Explainability by Design**: Machine learning predictive triage models feature automated bias monitoring across demographic vectors.
- **High-Throughput Offline-First**: Built with Service Worker caching and local IndexedDB sync for Tier-2/Tier-3 rural health sub-centres.
