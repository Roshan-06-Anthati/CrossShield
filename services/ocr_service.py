import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

# Point pytesseract to your Tesseract install location
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extracts text from a PDF - tries direct text first, falls back to OCR for scanned pages"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""

    for page in doc:
        # Try direct text extraction first (fast, works for normal PDFs)
        text = page.get_text()

        if text.strip():
            full_text += text + "\n"
        else:
            # Fallback: page has no extractable text (likely scanned/image) -> run OCR
            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            ocr_text = pytesseract.image_to_string(img)
            full_text += ocr_text + "\n"

    doc.close()
    return full_text.strip()