# AI/ML Clinical Risk Scoring & Algorithmic Fairness

## Model Pipeline
- **Inputs**: Demographic indicators, vitals (systolic/diastolic BP, SpO2, heart rate), lab test history, and existing comorbidities.
- **Outputs**:
  - Triage Priority (Low, Moderate, High, Critical)
  - 30-Day Hospital Readmission Probability
  - Sepsis & Diabetic Complication Early Warning Signals

## Fairness Metric Thresholds
- **Disparate Impact Ratio**: Monitored between 0.80 and 1.25 across gender, age brackets, and rural/urban geography.
- **Equalized Odds**: False Positive Rates (FPR) and False Negative Rates (FNR) validated within 5% tolerance across sub-populations.
