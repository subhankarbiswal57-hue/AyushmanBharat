// SMART-on-FHIR Clinical Frame & PostMessage Communication Bridge
// Enables Ayushman Bharat clinician triage station to be embedded inside hospital EHR systems (e.g. e-Hospital)
// Communicates bi-directionally without requiring context switching.

class EhrEmbedBridge {
  constructor(targetOrigin = "*") {
    this.targetOrigin = targetOrigin;
    this.context = {
      patientId: null,
      encounterId: null,
      practitionerId: null
    };
    this.handlers = new Map();
    this._listenToMessages();
  }

  _listenToMessages() {
    if (typeof window === "undefined") return;
    window.addEventListener("message", (event) => {
      if (this.targetOrigin !== "*" && event.origin !== this.targetOrigin) {
        console.warn(`[EhrEmbed] Blocked unauthorized message origin: ${event.origin}`);
        return;
      }

      const data = event.data;
      if (!data || !data.type) return;

      if (data.type === "EHR_SET_CONTEXT") {
        this.context = { ...this.context, ...data.payload };
        this._notify("contextChange", this.context);
      } else if (data.type === "EHR_REQUEST_TRIAGE_DATA") {
        this.sendToHost("EHR_RESPONSE_TRIAGE_DATA", {
          context: this.context,
          timestamp: Date.now()
        });
      }

      if (this.handlers.has(data.type)) {
        this.handlers.get(data.type)(data.payload);
      }
    });
  }

  on(event, callback) {
    this.handlers.set(event, callback);
  }

  _notify(event, payload) {
    if (this.handlers.has(event)) {
      this.handlers.get(event)(payload);
    }
  }

  sendToHost(actionType, payload) {
    if (typeof window === "undefined" || !window.parent) return;
    window.parent.postMessage({
      source: "AYUSHMAN_CLINICAL_STATION",
      type: actionType,
      payload,
      timestamp: Date.now()
    }, this.targetOrigin);
  }

  notifyTriageCompleted(assessment) {
    this.sendToHost("AYUSHMAN_TRIAGE_COMPLETED", {
      patientId: this.context.patientId,
      assessment,
      completedAt: new Date().toISOString()
    });
  }

  notifyVitalsUpdated(vitals) {
    this.sendToHost("AYUSHMAN_VITALS_UPDATED", {
      patientId: this.context.patientId,
      vitals
    });
  }
}

if (typeof window !== "undefined") {
  window.ehrBridge = new EhrEmbedBridge();
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { EhrEmbedBridge };
}
