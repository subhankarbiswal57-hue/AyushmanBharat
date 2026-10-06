// Guided Onboarding Wizard for Rural Healthcare Beneficiaries
// Designed with progressive disclosure, simplified steps, and visual confirmations.

const ONBOARDING_STEPS = [
  {
    stepId: 1,
    title: "Language Selection",
    description: "Choose your most comfortable spoken language (English, Hindi, or Odia).",
    icon: "🌐",
    field: "preferredLanguage"
  },
  {
    stepId: 2,
    title: "ABHA Number Verification",
    description: "Enter your 14-digit ABHA card number or mobile number linked with Aadhaar.",
    icon: "🪪",
    field: "abhaId"
  },
  {
    stepId: 3,
    title: "One-Time Password (OTP)",
    description: "Enter the 6-digit confirmation code sent to your registered mobile phone.",
    icon: "📱",
    field: "otpCode"
  },
  {
    stepId: 4,
    title: "Consent Preferences",
    description: "Decide whether doctors at nearby government health centers can view past prescriptions.",
    icon: "🛡️",
    field: "consentAgreed"
  }
];

class OnboardingWizard {
  constructor() {
    this.currentStep = 1;
    this.formData = {};
    this.isCompleted = localStorage.getItem("ayushman_onboarding_done") === "true";
  }

  getCurrentStepDetails() {
    return ONBOARDING_STEPS.find(s => s.stepId === this.currentStep) || ONBOARDING_STEPS[0];
  }

  submitStep(fieldValue) {
    const step = this.getCurrentStepDetails();
    this.formData[step.field] = fieldValue;

    if (this.currentStep < ONBOARDING_STEPS.length) {
      this.currentStep++;
      return { completed: false, nextStep: this.getCurrentStepDetails() };
    } else {
      this.isCompleted = true;
      localStorage.setItem("ayushman_onboarding_done", "true");
      return { completed: true, summary: this.formData };
    }
  }

  previousStep() {
    if (this.currentStep > 1) {
      this.currentStep--;
    }
    return this.getCurrentStepDetails();
  }

  reset() {
    this.currentStep = 1;
    this.formData = {};
    this.isCompleted = false;
    localStorage.removeItem("ayushman_onboarding_done");
  }
}

if (typeof window !== "undefined") {
  window.onboardingWizard = new OnboardingWizard();
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { OnboardingWizard, ONBOARDING_STEPS };
}
