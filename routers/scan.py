from fastapi import APIRouter
from pydantic import BaseModel
from services.orchestration_service import full_email_scan

router = APIRouter()

class ScanEmailRequest(BaseModel):
    text: str

@router.post("/email")
def scan_email(request: ScanEmailRequest):
    return full_email_scan(request.text)