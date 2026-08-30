from fastapi import APIRouter
from schemas.score_schema import UnifiedScoreRequest
from services.score_service import calculate_unified_risk_score

router = APIRouter()

@router.post("/calculate")
def calculate_score(request: UnifiedScoreRequest):
    return calculate_unified_risk_score(
        email_score=request.email_score,
        website_score=request.website_score,
        ocr_score=request.ocr_score,
        sandbox_score=request.sandbox_score,
        graph_score=request.graph_score,
    )