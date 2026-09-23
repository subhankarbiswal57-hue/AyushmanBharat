# Testing Strategy & Quality Assurance Guide

## Test Suites

### 1. Integration Tests (`tests/integration_test.py`)
Validates cross-service flows:
- User registration and token validation through API Gateway.
- Clinical record ingestion and FHIR serialization.
- Audit ledger hash verification.

### 2. Algorithmic Bias & Fairness Tests (`tests/test_fairness.py`)
- Evaluates model predictions against synthetic populations.
- Verifies disparate impact ratio doesn't breach regulatory limits.

### 3. Running Test Suites
```bash
# Run all automated tests
pytest tests/ -v
```
