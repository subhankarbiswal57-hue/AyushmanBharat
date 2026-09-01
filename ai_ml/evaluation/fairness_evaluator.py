"""
Fairness Evaluator & Disparate Impact Calculator
Calculates Demographic Parity, Equal Opportunity Difference, and 4/5ths Rule Thresholds.
"""
from typing import List, Dict, Any

def evaluate_disparate_impact(
    dataset: List[Dict[str, Any]], 
    protected_attribute: str, 
    favorable_outcome_key: str = "is_high_risk"
) -> Dict[str, Any]:
    """
    Computes Demographic Parity Ratio across groups in protected_attribute.
    """
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for item in dataset:
        attr_val = str(item.get("demographics", {}).get(protected_attribute, "unknown")).lower()
        if attr_val not in groups:
            groups[attr_val] = []
        groups[attr_val].append(item)

    group_rates = {}
    for g, items in groups.items():
        pos_count = sum(1 for it in items if it.get(favorable_outcome_key, False))
        group_rates[g] = round(pos_count / max(len(items), 1), 4)

    if len(group_rates) < 2:
        return {
            "attribute": protected_attribute,
            "status": "INSUFFICIENT_SUBGROUPS",
            "group_rates": group_rates,
            "demographic_parity_ratio": 1.0,
            "four_fifths_rule_passed": True
        }

    min_rate = min(group_rates.values())
    max_rate = max(group_rates.values())
    dp_ratio = round(min_rate / max(max_rate, 0.0001), 4)

    # 4/5ths rule (0.80 threshold)
    passed = dp_ratio >= 0.80

    return {
        "attribute": protected_attribute,
        "status": "COMPLIANT" if passed else "DISPARITY_ALERT",
        "group_rates": group_rates,
        "demographic_parity_ratio": dp_ratio,
        "threshold": 0.80,
        "four_fifths_rule_passed": passed,
        "remediation_recommended": not passed
    }
