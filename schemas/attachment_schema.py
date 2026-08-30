from pydantic import BaseModel

class AttachmentAnalysisResponse(BaseModel):
    extracted_text: str
    is_phishing: bool
    risk_score: float
    verdict: str