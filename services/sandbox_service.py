from playwright.sync_api import sync_playwright
from urllib.parse import urlparse

SUSPICIOUS_KEYWORDS = ["verify", "login", "secure", "account", "confirm", "password", "urgent"]


def get_domain(url: str) -> str:
    try:
        domain = urlparse(url).netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def inspect_url(url: str) -> dict:
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    actual_redirects = []
    error = None
    final_url = url
    page_title = ""

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            def track_response(response):
                if 300 <= response.status < 400:
                    actual_redirects.append(response.url)

            page.on("response", track_response)

            page.goto(url, timeout=15000, wait_until="domcontentloaded")
            final_url = page.url
            page_title = page.title()

            browser.close()

    except Exception as e:
        error = str(e)

    risk_score = 0
    reasons = []

    if error:
        risk_score += 20
        reasons.append(f"Could not fully load the page: {error[:100]}")

    original_domain = get_domain(url)
    redirect_domains = set(get_domain(r) for r in actual_redirects)
    redirect_domains.discard(original_domain)
    redirect_domains.discard("")

    if len(redirect_domains) >= 2:
        risk_score += 40
        reasons.append(f"Redirected across multiple unrelated domains: {', '.join(list(redirect_domains)[:3])} — strong phishing indicator")
    elif len(redirect_domains) == 1:
        risk_score += 10
        reasons.append(f"Redirected to a different domain: {list(redirect_domains)[0]}")

    combined_text = (final_url + " " + page_title).lower()
    matched_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in combined_text]
    if matched_keywords and len(redirect_domains) > 0:
        risk_score += 15
        reasons.append(f"Suspicious keywords found alongside cross-domain redirect: {', '.join(matched_keywords)}")
    elif matched_keywords:
        reasons.append(f"Keywords present but no other risk indicators: {', '.join(matched_keywords)} (informational only)")    

    risk_score = min(risk_score, 100)

    return {
        "original_url": url,
        "final_url": final_url,
        "page_title": page_title,
        "redirect_count": len(actual_redirects),
        "cross_domain_redirects": list(redirect_domains),
        "risk_score": risk_score,
        "is_suspicious": risk_score > 0,
        "reasons": reasons if reasons else ["No suspicious behavior detected"],
        "error": error
    }