# CrossShield — Multi-Signal Fraud Detection Platform

A 5-layer fraud detection system that analyzes emails, URLs, and PDF attachments for phishing and fraud indicators, combining results into a single unified risk score.

## Live Demo

Backend deployed at: **https://crossshield.onrender.com** ([API docs](https://crossshield.onrender.com/docs))

Layers 1 (email classification), 2 (typosquatting), 3 (OCR), and 5 (graph correlation) run live on this deployment. **Layer 4 (URL sandboxing)** requires a real headless browser with OS-level dependencies that aren't reliably available on free-tier hosting — it is fully functional when run locally (see Quick Start below), but is skipped in the hosted demo. This is a hosting-environment constraint, not a code issue; the fix would be a custom Docker image with Chromium's system dependencies pre-installed.

## Quick Start (run locally — recommended for full functionality, including Layer 4)

```bash
git clone https://github.com/Roshan-06-Anthati/CrossShield.git
cd CrossShield

python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

pip install -r requirements.txt
playwright install chromium

uvicorn main:app --reload
```
Backend runs at `http://127.0.0.1:8000` (docs at `/docs`). Trained model files are included in the repo, so no retraining is needed to run the app.

In a second terminal:
```bash
cd frontend
npm install
npm run dev
```
Dashboard runs at `http://localhost:3000`.

Tesseract OCR must be installed separately (not a pip package) for Layer 3/OCR to work — see the Setup section below for OS-specific instructions.

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
- **Frontend:** Next.js, Tailwind CSS

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

### Run the frontend
```bash
cd frontend
npm install
npm run dev
```
Dashboard available at `http://localhost:3000`. Supports two modes: pasting raw email text, or uploading a PDF attachment.

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

## Testing & Real Issues Found

Each layer was stress-tested against real inputs (not just synthetic examples), which surfaced three concrete bugs — fixed and re-verified rather than left in place:

1. **Leetspeak bypass in Layer 2** — `paypa1-secure-verify.tk` (digit `1` instead of letter `l`) initially scored only 30% risk, missing the PayPal impersonation entirely. Fixed by normalizing common character substitutions (`0→o`, `1→l`, `3→e`, etc.) before comparison. Score for that exact domain improved from 30% to 90%.

2. **`www.` prefix false positive in Layer 2** — `www.google.com` was flagged as "closely resembling but not matching" `google.com`, since the raw strings differ. Fixed by stripping the `www.` prefix before comparison. This also mirrors an earlier, separately-discovered instance of the same bug pattern in Layer 4 (see below), rather than being copy-pasted from that fix.

3. **Weight dilution in the unified score** — a clear-cut scam email with no URL (classic "inheritance fund" wording) was independently classified as 79.66% phishing by Layer 1, but the *unified* score came out to only 23.9% ("Low Risk"), because the scoring formula applied Layer 1's fixed 30% weight regardless of whether other layers had anything to contribute. Fixed by dynamically redistributing weights across only the layers that actually ran for a given input; the same email now correctly scores 79.66% overall.

Layer 4 (sandboxing) went through a similar iteration earlier: an initial version counted every network request as a "redirect" (falsely flagging Google's homepage), then a corrected version still flagged Microsoft's real `www.` redirect and a legitimate bank's use of the word "account" — both fixed by requiring genuine cross-domain redirects and treating keywords as corroborating evidence only, not a standalone signal.

## Known Limitations & Future Work

- **No known-malicious-URL database integration** (e.g., Google Safe Browsing, VirusTotal) — Layer 4 detects a specific technique (redirect cloaking), not general URL reputation
- **No WHOIS/domain-age checking** — deliberately excluded due to live network calls being slow and rate-limited; would strengthen Layer 2 if added
- **No homoglyph (Unicode lookalike) detection** — current normalization handles leetspeak substitutions but not visually-identical Unicode characters from different scripts
- **In-memory graph** — Layer 5's graph resets on server restart; would need persistent storage (database-backed graph) for production use
- **OCR layer's classification accuracy is bounded by Layer 1's training data** — reliable on email-like text, not general documents
- **Layer 4 does not yet capture a screenshot of the sandboxed page** — would let a user visually verify a suspicious page instead of relying solely on the automated score; identified as a good next addition but not yet built
- **No automated test suite** — layers were validated through extensive manual testing (documented above) rather than `pytest`-based unit tests; adding these would make regressions easier to catch automatically
- **No deployment** — currently runs locally only; a live-hosted version (e.g., Render + Vercel) has not been set up

## Project Status

Backend: complete — all 5 layers built, individually tested, and validated end-to-end through the orchestration endpoint.
Frontend: complete — supports both email text and PDF attachment scanning, with results displayed in real time.

## Disclosure

This project was built as a learning exercise, inspired by a 5-layer fraud detection concept. All code, model training, and testing in this repository were done independently.
