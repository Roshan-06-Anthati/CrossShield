from fastapi import APIRouter
from pydantic import BaseModel
from services.typosquat_service import check_typosquatting

router = APIRouter()

class WebsiteRequest(BaseModel):
    domain: str

@router.post("/analyze")
def analyze_website(request: WebsiteRequest):
    return check_typosquatting(request.domain)