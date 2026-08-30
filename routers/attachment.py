from fastapi import APIRouter, UploadFile, File
from services.ocr_service import extract_text_from_pdf
from services.email_service import analyze_email_text

router = APIRouter()


@router.post("/analyze")
async def analyze_attachment(file: UploadFile = File(...)):
    pdf_bytes = await file.read()
    extracted_text = extract_text_from_pdf(pdf_bytes)

    if not extracted_text.strip():
        return {
            "extracted_text": "",
            "is_phishing": False,
            "risk_score": 0.0,
            "verdict": "No text could be extracted"
        }

    result = analyze_email_text(extracted_text)
    result["extracted_text"] = extracted_text[:500]
    return result