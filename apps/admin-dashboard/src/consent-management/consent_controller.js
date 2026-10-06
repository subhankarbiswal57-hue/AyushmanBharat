// DPDP (Digital Personal Data Protection) Consent Lifecycle Registry Controller
// Handles consent artefact validation, purpose specification, time expiry, and immediate revocation audits.

const CONSENT_PURPOSES = {
  CARE: "Direct Clinical Healthcare Delivery & Treatment",
  RESEARCH: "Anonymized Public Health Epidemiological Research",
  EMERGENCY: "Trauma & Critical Emergency Care (Automatic Life-Threatening Override)",
  INSURANCE: "Ayushman Bharat PM-JAY Claim Processing"
};

class ConsentRegistryManager {
  constructor() {
    this.records = new Map();
  }

  registerConsent(patientId, abhaId, purpose, expiryDays = 365, hiuId = "HIU-ALL") {
    if (!CONSENT_PURPOSES[purpose]) {
      throw new Error(`Invalid DPDP Purpose code: ${purpose}`);
    }

    const consentId = `ARTEFACT-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
    const grantedAt = Date.now();
    const expiresAt = grantedAt + (expiryDays * 86400 * 1000);

    const record = {
      consentId,
      patientId,
      abhaId,
      purpose,
      purposeDescription: CONSENT_PURPOSES[purpose],
      hiuId,
      status: "ACTIVE",
      grantedAt,
      expiresAt,
      revokedAt: null
    };

    this.records.set(consentId, record);
    return record;
  }

  isConsentValid(consentId) {
    const rec = this.records.get(consentId);
    if (!rec) return false;
    if (rec.status !== "ACTIVE") return false;
    if (Date.now() > rec.expiresAt) {
      rec.status = "EXPIRED";
      return false;
    }
    return true;
  }

  revokeConsent(consentId, reason = "Beneficiary Opt-Out") {
    const rec = this.records.get(consentId);
    if (!rec) {
      return { success: false, message: "Consent artefact not found" };
    }

    rec.status = "REVOKED";
    rec.revokedAt = Date.now();
    rec.revocationReason = reason;

    return {
      success: true,
      consentId,
      status: "REVOKED",
      revokedAt: rec.revokedAt,
      message: "Consent successfully withdrawn under DPDP statutory guidelines"
    };
  }

  listConsents(filterStatus = null) {
    const all = Array.from(this.records.values());
    if (filterStatus) {
      return all.filter(r => r.status === filterStatus);
    }
    return all;
  }
}

if (typeof window !== "undefined") {
  window.consentRegistry = new ConsentRegistryManager();
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { ConsentRegistryManager, CONSENT_PURPOSES };
}
