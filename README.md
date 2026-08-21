# healthtech-platform

Equity-first, AI-assisted care delivery infrastructure. Multi-sided platform (patients, clinicians, health systems) that treats digital exclusion, privacy/security, algorithmic bias, workflow burden, and interoperability as first-class architecture concerns rather than afterthoughts.

## Risk area → folder ownership

| Risk Area | Folder Owner |
|---|---|
| Digital exclusion / equity | `apps/patient-frontend/` |
| Privacy & security | `services/auth-service/` |
| AI/algorithmic bias | `ai-ml/` |
| Workflow / clinician burden | `apps/clinician-frontend/` |
| Interoperability / fragmentation | `services/api-gateway/` |
| Governance (cross-cutting) | `apps/admin-dashboard/` + `services/audit-logging/` + `docs/governance/` |

## Structure

```
healthtech-platform/
├── apps/
│   ├── patient-frontend/      # equity & access
│   ├── clinician-frontend/    # workflow burden
│   └── admin-dashboard/       # governance
├── services/
│   ├── api-gateway/           # interoperability
│   ├── auth-service/          # privacy & security
│   ├── core-backend/          # core business logic
│   └── audit-logging/         # cross-cutting, feeds governance
├── ai-ml/                     # AI fairness layer
├── infra/                     # deployment, security policy, compliance
├── shared/                    # design system, shared types
└── docs/                      # governance, equity checklist, standards
```

Each leaf folder has its own `README.md` describing what belongs there. This is a scaffold — no code yet, just the structure and ownership map so the risk areas get built in from day one instead of bolted on later.

## Notes

- Governance is deliberately spread across three places (dashboard, logging service, docs) rather than one, since it's the piece that tends to fall through the cracks when not explicitly assigned.
- `services/api-gateway/` and `services/auth-service/` should be developed in lockstep — more interoperability surface area means more security surface area.
- Pick one wedge risk area to build/launch around first rather than all five simultaneously.
