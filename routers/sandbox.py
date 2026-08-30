from fastapi import APIRouter
from schemas.sandbox_schema import SandboxRequest
from services.sandbox_service import inspect_url

router = APIRouter()

@router.post("/analyze")
def analyze_url(request: SandboxRequest):
    return inspect_url(request.url)