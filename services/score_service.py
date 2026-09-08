def calculate_unified_risk_score(
    email_score: float = 0,
    website_score: float = 0,
    ocr_score: float = 0,
    sandbox_score: float = 0,
    graph_score: float = 0,
    active_layers: list[str] = None,
) -> dict:
    all_weights = {
        "email": 0.30,
        "website": 0.25,
        "ocr": 0.15,
        "sandbox": 0.20,
        "graph": 0.10,
    }

    scores = {
        "email": email_score,
        "website": website_score,
        "ocr": ocr_score,
        "sandbox": sandbox_score,
        "graph": graph_score,
    }

    # If not explicitly told which layers ran, infer it: a layer is "active"
    # if it has a non-zero score OR was explicitly passed
    if active_layers is None:
        active_layers = [k for k, v in scores.items() if v > 0] or ["email"]

    # Redistribute weights proportionally across only the active layers
    active_weight_sum = sum(all_weights[k] for k in active_layers)
    normalized_weights = {
        k: (all_weights[k] / active_weight_sum if k in active_layers else 0)
        for k in all_weights
    }

    weighted_total = sum(scores[k] * normalized_weights[k] for k in scores)
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
        "breakdown": {f"{k}_contribution": round(scores[k] * normalized_weights[k], 2) for k in scores},
        "weights_used": normalized_weights,
        "active_layers": active_layers,
    }