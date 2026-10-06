// Accessibility (a11y) & Low-Literacy Support Engine
// Provides high-contrast modes, scalable font controls, text-to-speech audio feedback,
// and iconographic assistive visual hints for rural beneficiaries.

class AccessibilityEnhancer {
  constructor() {
    this.highContrast = localStorage.getItem("a11y_high_contrast") === "true";
    this.fontSizeScale = parseFloat(localStorage.getItem("a11y_font_scale") || "1.0");
    this.speechSynthesisAvailable = typeof window !== "undefined" && "speechSynthesis" in window;
    this.init();
  }

  init() {
    if (typeof document === "undefined") return;
    this.applyContrast();
    this.applyFontScale();
  }

  toggleHighContrast() {
    this.highContrast = !this.highContrast;
    localStorage.setItem("a11y_high_contrast", this.highContrast);
    this.applyContrast();
    return this.highContrast;
  }

  applyContrast() {
    if (typeof document === "undefined") return;
    if (this.highContrast) {
      document.documentElement.classList.add("a11y-high-contrast");
    } else {
      document.documentElement.classList.remove("a11y-high-contrast");
    }
  }

  setFontScale(scale) {
    this.fontSizeScale = Math.min(Math.max(scale, 0.8), 1.6);
    localStorage.setItem("a11y_font_scale", this.fontSizeScale);
    this.applyFontScale();
    return this.fontSizeScale;
  }

  increaseFontSize() {
    return this.setFontScale(this.fontSizeScale + 0.15);
  }

  decreaseFontSize() {
    return this.setFontScale(this.fontSizeScale - 0.15);
  }

  applyFontScale() {
    if (typeof document === "undefined") return;
    document.documentElement.style.setProperty("--a11y-font-scale", `${this.fontSizeScale}`);
  }

  speakText(text, lang = "en-IN") {
    if (!this.speechSynthesisAvailable || !text) return false;
    window.speechSynthesis.cancel(); // Stop prior speech
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    utterance.rate = 0.9; // Slightly slower for clear comprehension
    window.speechSynthesis.speak(utterance);
    return true;
  }
}

if (typeof window !== "undefined") {
  window.a11yEnhancer = new AccessibilityEnhancer();
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { AccessibilityEnhancer };
}
