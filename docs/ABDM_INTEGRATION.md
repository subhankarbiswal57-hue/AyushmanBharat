# Ayushman Bharat Digital Mission (ABDM) Integration Guide

This guide details implementation of ABDM M1, M2, and M3 milestones for the platform.

## Milestones Overview

### Milestone M1: ABHA (Ayushman Bharat Health Account) Issuance & Verification
- Generation of 14-digit ABHA Number via Aadhaar OTP or Mobile OTP.
- ABHA address (`<username>@abdm`) linkage.
- Verification and demographic authentication against NHA UIDAI/ABDM Gateway.

### Milestone M2: Health Facility & Healthcare Professional Registry (HFR / HPR)
- Facility onboarding with official Hospital Registry (NIN / HFR ID).
- Clinician credential verification with Medical Council / HPR ID.

### Milestone M3: Health Information Provider (HIP) & User (HIU) Consent Flows
- Consent Manager integration (`/v0.5/consent-requests/init`).
- Cryptographic key exchange for encrypted health records (Diffie-Hellman + AES-GCM).
- FHIR R4 Bundle composition for Diagnostic Reports, Prescriptions, and Discharge Summaries.
