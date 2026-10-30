# API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/beneficiary/{id} | Fetch beneficiary details |
| POST | /api/v1/enroll | Enroll new beneficiary |
| POST | /api/v1/claim/submit | Submit new insurance claim |
| GET | /api/v1/claim/{id}/status | Check claim adjudication status |
| PUT | /api/v1/claim/{id} | Update claim status |
| GET | /api/v1/hospitals | List empanelled hospitals |
| POST | /api/v1/consent/request | Initiate DPDP statutory consent request |
| GET | /api/v1/consent/{id} | Retrieve consent artefact details |
| POST | /api/v1/consent/{id}/revoke | Revoke active patient consent |

### Health Facility Registry (HFR) Endpoints
- `GET /api/v1/hfr/facilities`: Search registered healthcare facilities by pincode and district.
- `GET /api/v1/hfr/facilities/{facility_id}`: Retrieve detailed facility profile and verified department metadata.
