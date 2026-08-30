def calculate_unified_risk_score(
    email_score: float = 0,
    website_score: float = 0,
    ocr_score: float = 0,
    sandbox_score: float = 0,
    graph_score: float = 0,
) -> dict:
    """
    Combines risk scores from all 5 layers into one unified score.
    Weights reflect how strong/reliable each signal is, based on
    what we found during testing:
    - Email (Layer 1): highest weight - most reliable, real ML metrics (98% accuracy)
    - Website/typosquat (Layer 2): strong, well-tested rule-based signal
    - OCR (Layer 3): moderate - inherits Layer 1's reliability, but has known
      out-of-distribution issues on non-email documents
    - Sandbox (Layer 4): moderate - good at redirect-cloaking specifically,
      not a general malicious-URL scanner
    - Graph (Layer 5): supporting signal - strengthens confidence when a
      campaign pattern is detected, but rarely used alone
    """
    weights = {
        "email": 0.30,
        "website": 0.25,
        "ocr": 0.15,
        "sandbox": 0.20,
        "graph": 0.10,
    }

    weighted_total = (
        email_score * weights["email"]
        + website_score * weights["website"]
        + ocr_score * weights["ocr"]
        + sandbox_score * weights["sandbox"]
        + graph_score * weights["graph"]
    )

    final_score = round(weighted_total, 2)

    if final_score >= 70:
        verdict = "High Risk - Likely Fraudulent"
    elif final_score >= 40:
        verdict = "Medium Risk - Review Recommended"
    else:
        verdict = "Low Risk - Likely Legitimate"

    return {
        "final_risk_score": final_score,
        "verdict": verdict,
        "breakdown": {
            "email_contribution": round(email_score * weights["email"], 2),
            "website_contribution": round(website_score * weights["website"], 2),
            "ocr_contribution": round(ocr_score * weights["ocr"], 2),
            "sandbox_contribution": round(sandbox_score * weights["sandbox"], 2),
            "graph_contribution": round(graph_score * weights["graph"], 2),
        },
        "weights_used": weights
    }