from pydantic import BaseModel

class UnifiedScoreRequest(BaseModel):
    email_score: float = 0
    website_score: float = 0
    ocr_score: float = 0
    sandbox_score: float = 0
    graph_score: float = 0