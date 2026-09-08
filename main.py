from fastapi import FastAPI
from pydantic import BaseModel
from routers import website, attachment, sandbox, graph, score
from services.email_service import analyze_email_text
from routers import website, attachment, sandbox, graph, score, scan
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Fraud Detection Platform")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailRequest(BaseModel):
    text: str

# ---- Register all routers here, grouped together ----
app.include_router(website.router, prefix="/api/website", tags=["website"])
app.include_router(attachment.router, prefix="/api/attachment", tags=["attachment"])
app.include_router(sandbox.router, prefix="/api/sandbox", tags=["sandbox"])
app.include_router(graph.router, prefix="/api/graph", tags=["graph"])
app.include_router(score.router, prefix="/api/score", tags=["score"])
app.include_router(scan.router, prefix="/api/scan", tags=["scan"])


@app.get("/")
def health():
    return {"status": "running"}


@app.post("/api/email/analyze")
def analyze_email(request: EmailRequest):
    return analyze_email_text(request.text)




















# from fastapi import FastAPI
# from pydantic import BaseModel
# from routers import website
# from routers import website, attachment
# from routers import website, attachment, sandbox, graph
# from routers import website, attachment, sandbox, graph, score
# import joblib
# from pathlib import Path
# from routers import website, attachment, sandbox

# app = FastAPI(title="Fraud Detection Platform")

# BASE_DIR = Path(__file__).resolve().parent
# MODEL_DIR = BASE_DIR / 'models'

# # Load the trained model and vectorizer once, when the server starts
# model = joblib.load(MODEL_DIR / 'phishing_model.pkl')
# vectorizer = joblib.load(MODEL_DIR / 'vectorizer.pkl')

# class EmailRequest(BaseModel):
#     text: str

# app.include_router(website.router, prefix="/api/website", tags=["website"])
# app.include_router(attachment.router, prefix="/api/attachment", tags=["attachment"])
# app.include_router(sandbox.router, prefix="/api/sandbox", tags=["sandbox"])
# app.include_router(graph.router, prefix="/api/graph", tags=["graph"])
# app.include_router(score.router, prefix="/api/score", tags=["score"])


# @app.get("/")
# def health():
#     return {"status": "running"}

# @app.post("/api/email/analyze")
# def analyze_email(request: EmailRequest):
#     features = vectorizer.transform([request.text])
#     prediction = model.predict(features)[0]
#     probability = model.predict_proba(features)[0]

#     is_phishing = bool(prediction == 1)
#     risk_score = round(float(probability[1]) * 100, 2)

#     return {
#         "is_phishing": is_phishing,
#         "risk_score": risk_score,
#         "verdict": "Phishing" if is_phishing else "Legitimate"
#     }