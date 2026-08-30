# CrossShield — Multi-Signal Fraud Detection Platform

A 5-layer fraud detection system that analyzes emails, URLs, and PDF attachments for phishing and fraud indicators, combining results into a single unified risk score.

## What it does

CrossShield takes a suspicious email, URL, or PDF attachment and runs it through multiple independent detection layers, each targeting a different fraud technique. Rather than relying on one signal, it correlates findings across layers — and across scans — to catch coordinated fraud campaigns that a single check would miss.

## Architecture

```
Input (email / URL / PDF)
        │
        ▼
┌───────────────────────────────────────────┐
│  Layer 1: Email Classification (XGBoost)   │
│  Layer 2: Typosquatting Detection          │
│  Layer 3: PDF OCR + Text Extraction        │
│  Layer 4: URL Sandboxing                   │
│  Layer 5: Graph Correlation (NetworkX)     │
└───────────────────────────────────────────┘
        │
        ▼
  Unified Risk Score (weighted combination)
```

An orchestration layer (`/api/scan/email`) automatically runs an email through Layer 1, extracts any URLs it contains, runs those through Layers 2 and 4, logs them to the Layer 5 graph, and returns one combined verdict.

## Layers, in detail

### Layer 1 — Email Phishing Classification
Trained an XGBoost classifier on ~82,000 labeled emails (a combined dataset of Enron, Ling, CEAS, Nazario, Nigerian Fraud, and SpamAssassin corpora), using TF-IDF text vectorization.

**Real evaluation metrics (held-out test set, 16,498 emails):**
- Accuracy: 98%
- Precision (phishing class): 97%
- Recall (phishing class): 99%

### Layer 2 — Typosquatting Detection
Rule-based detection comparing submitted domains against a list of commonly impersonated brands, using:
- String similarity scoring
- Substring-based brand detection (catches embedded brand names like `paypal-secure-verify.com`)
- **Leetspeak/lookalike character normalization** (`0→o`, `1→l`, `3→e`, etc.) — added after testing revealed domains like `paypa1.com` were being missed
- Suspicious TLD flagging (`.tk`, `.xyz`, `.ml`, and similar free/commonly-abused domains)

Iteratively stress-tested against real domains (Google, Microsoft, SBI, Amazon, Netflix, Facebook) to eliminate false positives before arriving at the current logic.

### Layer 3 — PDF OCR
Extracts text from PDF attachments using direct text extraction (PyMuPDF) with OCR fallback (Tesseract) for scanned/image-based pages. Extracted text is classified using the same Layer 1 model.

**Known limitation:** the underlying model was trained exclusively on email text. Structurally different documents (e.g., resumes) are out-of-distribution input and can produce unreliable, low-confidence predictions. This layer is reliable for email-like content specifically, not general-purpose document classification.

### Layer 4 — URL Sandboxing
Opens submitted URLs in an isolated headless browser (Playwright) and analyzes behavior rather than static content:
- Tracks HTTP-level cross-domain redirects (the core signal — legitimate sites redirect within their own domain; phishing links often cloak their destination through unrelated domains)
- Flags suspicious keywords only when combined with a cross-domain redirect, since keywords alone (e.g., "account," "verify") produce false positives on legitimate sites

**Known limitation:** only tracks HTTP-level redirects, not JavaScript-triggered redirects. Does not check against known-malicious-URL databases (e.g., Google Safe Browsing) or scan page content/downloads.

### Layer 5 — Graph Correlation
Builds a graph (NetworkX) connecting scanned entities (email senders, domains) as they're processed. Identifies connected clusters — if multiple distinct scans link to the same infrastructure, it surfaces this as a likely coordinated campaign rather than isolated incidents.

### Unified Risk Score
Combines all layer outputs into one weighted score:

| Layer | Weight |
|---|---|
| Email | 30% |
| Website/Typosquat | 25% |
| Sandbox | 20% |
| OCR | 15% |
| Graph | 10% |

Weights reflect relative signal reliability established during testing — email classification has the strongest empirical backing (formal accuracy/precision/recall), so it's weighted highest.

## Tech Stack

- **Backend:** Python, FastAPI
- **ML:** XGBoost, scikit-learn, pandas
- **OCR:** Tesseract, PyMuPDF
- **Browser automation:** Playwright
- **Graph analysis:** NetworkX
- **Frontend:** Next.js *(in progress)*

## Setup

```bash
# Clone and enter the project
git clone <repo-url>
cd fraud-detection-platform

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Install Tesseract OCR separately (not a pip package):
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Mac: brew install tesseract
# Linux: sudo apt install tesseract-ocr
```

### Dataset
This project uses the [Phishing Email Dataset](https://www.kaggle.com/datasets/naserabdullahalam/phishing-email-dataset) (Kaggle). Download it and place the CSVs in a `data/` folder before training.

### Train the model
```bash
python scripts/train_model.py
```
This trains the classifier and saves it to `models/`.

### Run the API
```bash
uvicorn main:app --reload
```
API docs available at `http://127.0.0.1:8000/docs`

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/email/analyze` | POST | Classify raw email text |
| `/api/website/analyze` | POST | Check a domain for typosquatting |
| `/api/attachment/analyze` | POST | Extract and classify text from a PDF |
| `/api/sandbox/analyze` | POST | Inspect a URL's redirect behavior |
| `/api/graph/add` | POST | Add a node to the correlation graph |
| `/api/graph/campaigns` | GET | List detected campaign clusters |
| `/api/score/calculate` | POST | Combine layer scores into a unified verdict |
| `/api/scan/email` | POST | Full pipeline: email → all applicable layers → unified score |

## Known Limitations & Future Work

- **No known-malicious-URL database integration** (e.g., Google Safe Browsing, VirusTotal) — Layer 4 detects a specific technique (redirect cloaking), not general URL reputation
- **No WHOIS/domain-age checking** — deliberately excluded due to live network calls being slow and rate-limited; would strengthen Layer 2 if added
- **No homoglyph (Unicode lookalike) detection** — current normalization handles leetspeak substitutions but not visually-identical Unicode characters from different scripts
- **In-memory graph** — Layer 5's graph resets on server restart; would need persistent storage (database-backed graph) for production use
- **OCR layer's classification accuracy is bounded by Layer 1's training data** — reliable on email-like text, not general documents
- **Frontend dashboard** — in progress

## Project Status

Backend: complete and tested across all 5 layers, individually and via the orchestration endpoint.
Frontend: in progress.

## Disclosure

This project was built as a learning exercise, inspired by a 5-layer fraud detection concept. All code, model training, and testing in this repository were done independently.
