// Clinical Alert Fatigue Reducer & Priority Notification Engine
// Filters noise, suppresses redundant duplicate notifications, and escalates true emergencies (NEWS2 score >= 7)

class AlertFatigueReducer {
  constructor(cooldownMs = 300000) { // 5-minute deduplication cooldown
    this.cooldownMs = cooldownMs;
    this.recentAlerts = new Map();
  }

  calculateNEWS2(vitals) {
    let score = 0;
    const { heartRate, spo2, systolicBp, respRate, temp } = vitals;

    // Respiration rate
    if (respRate) {
      if (respRate <= 8 || respRate >= 25) score += 3;
      else if (respRate >= 21) score += 2;
      else if (respRate <= 11) score += 1;
    }

    // SpO2
    if (spo2) {
      if (spo2 <= 91) score += 3;
      else if (spo2 <= 93) score += 2;
      else if (spo2 <= 95) score += 1;
    }

    // Systolic Blood Pressure
    if (systolicBp) {
      if (systolicBp <= 90 || systolicBp >= 220) score += 3;
      else if (systolicBp <= 100) score += 2;
      else if (systolicBp <= 110) score += 1;
    }

    // Heart Rate
    if (heartRate) {
      if (heartRate <= 40 || heartRate >= 131) score += 3;
      else if (heartRate >= 111) score += 2;
      else if (heartRate <= 50 || heartRate >= 91) score += 1;
    }

    // Temperature
    if (temp) {
      if (temp <= 95.0) score += 3;
      else if (temp >= 102.4) score += 2;
      else if (temp <= 96.8 || temp >= 100.4) score += 1;
    }

    return score;
  }

  evaluateAlert(patientId, alertType, vitals, severity = "INFO") {
    const news2 = vitals ? this.calculateNEWS2(vitals) : 0;
    const key = `${patientId}_${alertType}`;
    const now = Date.now();

    // Critical escalation override: always trigger immediately if NEWS2 >= 7 or Red Triage
    if (news2 >= 7 || severity === "CRITICAL" || severity === "EMERGENCY") {
      this.recentAlerts.set(key, now);
      return {
        shouldDisplay: true,
        urgency: "HIGH_CRITICAL",
        news2Score: news2,
        action: "IMMEDIATE_BEDSIDE_ASSESSMENT",
        suppressed: false
      };
    }

    // Check cooldown for non-emergency alerts to prevent fatigue
    if (this.recentAlerts.has(key)) {
      const lastAlertTime = this.recentAlerts.get(key);
      if (now - lastAlertTime < this.cooldownMs) {
        return {
          shouldDisplay: false,
          urgency: "SUPPRESSED_COOLDOWN",
          news2Score: news2,
          suppressed: true,
          nextEligibleInSeconds: Math.ceil((this.cooldownMs - (now - lastAlertTime)) / 1000)
        };
      }
    }

    this.recentAlerts.set(key, now);
    return {
      shouldDisplay: true,
      urgency: news2 >= 5 ? "MEDIUM_URGENT" : "LOW_ROUTINE",
      news2Score: news2,
      action: news2 >= 5 ? "PROMPT_TRIAGE_REVIEW" : "STANDARD_MONITORING",
      suppressed: false
    };
  }

  clearHistory() {
    this.recentAlerts.clear();
  }
}

if (typeof window !== "undefined") {
  window.alertReducer = new AlertFatigueReducer();
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { AlertFatigueReducer };
}
