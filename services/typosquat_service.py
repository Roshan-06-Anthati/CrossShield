from difflib import SequenceMatcher

# Well-known brands to protect against impersonation
KNOWN_DOMAINS = [
    "paypal.com", "amazon.com", "google.com", "microsoft.com",
    "apple.com", "facebook.com", "netflix.com", "chase.com",
    "bankofamerica.com", "hdfcbank.com", "icicibank.com", "sbi.co.in",
    "phonepe.com", "paytm.com", "flipkart.com", "instagram.com",
    "linkedin.com", "whatsapp.com", "gmail.com", "outlook.com"
]

# TLDs commonly abused for phishing (free/cheap to register)
SUSPICIOUS_TLDS = [".tk", ".xyz", ".ml", ".ga", ".cf", ".gq", ".top", ".club"]

# Common leetspeak / lookalike character substitutions
LEETSPEAK_MAP = str.maketrans({
    '0': 'o', '1': 'l', '3': 'e', '4': 'a', '5': 's', '7': 't', '@': 'a'
})


def normalize_domain(domain: str) -> str:
    """Converts common character substitutions back to normal letters"""
    return domain.translate(LEETSPEAK_MAP)


def similarity_ratio(a: str, b: str) -> float:
    """Returns a similarity score between 0 and 1"""
    return SequenceMatcher(None, a, b).ratio()


def check_typosquatting(domain: str) -> dict:
    domain = domain.lower().strip()
    if domain.startswith("www."):
        domain = domain[4:]
    normalized = normalize_domain(domain)

    best_match = None
    best_score = 0.0
    matched_on_normalized = False

    for known in KNOWN_DOMAINS:
        # Check both the raw domain AND the normalized (de-leetspeak'd) version
        raw_score = similarity_ratio(domain, known)
        norm_score = similarity_ratio(normalized, known)

        if raw_score > best_score:
            best_score = raw_score
            best_match = known
            matched_on_normalized = False

        if norm_score > best_score:
            best_score = norm_score
            best_match = known
            matched_on_normalized = True

    is_exact_match = domain in KNOWN_DOMAINS
    is_suspicious_similarity = (not is_exact_match) and (best_score > 0.75)

    # Substring check - also check normalized version for embedded brand names
    brand_embedded_match = None
    matched_brand_on_normalized = False
    for known in KNOWN_DOMAINS:
        brand_name = known.split('.')[0]
        if len(brand_name) <= 3:
            continue
        if brand_name in domain and domain != known:
            brand_embedded_match = known
            break
        if brand_name in normalized and domain != known:
            brand_embedded_match = known
            matched_brand_on_normalized = True
            break

    has_suspicious_tld = any(domain.endswith(tld) for tld in SUSPICIOUS_TLDS)

    risk_score = 0
    reasons = []

    if is_suspicious_similarity:
        risk_score += 70
        note = " (detected after normalizing lookalike characters, e.g. 0→o, 1→l)" if matched_on_normalized else ""
        reasons.append(f"Domain closely resembles '{best_match}' but is not an exact match{note}")
    elif brand_embedded_match:
        risk_score += 60
        note = " (detected after normalizing lookalike characters)" if matched_brand_on_normalized else ""
        reasons.append(f"Domain contains brand name from '{brand_embedded_match}' with additional text — common impersonation pattern{note}")

    if has_suspicious_tld:
        risk_score += 30
        reasons.append("Domain uses a commonly abused top-level domain")

    risk_score = min(risk_score, 100)

    return {
        "domain": domain,
        "is_suspicious": risk_score > 0,
        "risk_score": risk_score,
        "closest_known_match": best_match if (is_suspicious_similarity or brand_embedded_match) else None,
        "similarity_score": round(best_score, 2),
        "reasons": reasons if reasons else ["No suspicious patterns detected"]
    }