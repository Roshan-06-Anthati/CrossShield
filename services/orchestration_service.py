import re
from services.email_service import analyze_email_text  # we'll extract this as a reusable function
from services.typosquat_service import check_typosquatting
from services.sandbox_service import inspect_url
from services.graph_service import add_scan_result
from services.score_service import calculate_unified_risk_score


def extract_urls(text: str) -> list[str]:
    """Simple regex to find URLs in email text"""
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
    return re.findall(url_pattern, text)


def full_email_scan(email_text: str) -> dict:
    # Layer 1: Email classification
    email_result = analyze_email_text(email_text)

    # Extract any URLs found in the email
    urls = extract_urls(email_text)

    website_score = 0
    sandbox_score = 0
    website_results = []
    sandbox_results = []

    for url in urls[:3]:  # limit to first 3 URLs to avoid slow requests
        domain = url.replace("https://", "").replace("http://", "").split("/")[0]

        # Layer 2: Typosquatting check
        typosquat_result = check_typosquatting(domain)
        website_results.append(typosquat_result)
        website_score = max(website_score, typosquat_result["risk_score"])

        # Layer 4: Sandbox check
        sandbox_result = inspect_url(url)
        sandbox_results.append(sandbox_result)
        sandbox_score = max(sandbox_score, sandbox_result["risk_score"])

        # Layer 5: Add to graph for correlation
        add_scan_result(
            node_type="domain",
            node_id=domain,
            related_to=[],
            risk_score=max(typosquat_result["risk_score"], sandbox_result["risk_score"])
        )

    # Calculate unified score
    # unified = calculate_unified_risk_score(
    #     email_score=email_result["risk_score"],
    #     website_score=website_score,
    #     ocr_score=0,
    #     sandbox_score=sandbox_score,
    #     graph_score=0
    # )
    active_layers = ["email"]
    if urls:
        active_layers.extend(["website", "sandbox"])

    unified = calculate_unified_risk_score(
        email_score=email_result["risk_score"],
        website_score=website_score,
        ocr_score=0,
        sandbox_score=sandbox_score,
        graph_score=0,
        active_layers=active_layers
    )

    return {
        "email_analysis": email_result,
        "urls_found": urls,
        "website_analysis": website_results,
        "sandbox_analysis": sandbox_results,
        "unified_result": unified
    }