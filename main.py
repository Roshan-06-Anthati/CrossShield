from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from routers import website, attachment, sandbox, graph, score, scan
from services.email_service import analyze_email_text

app = FastAPI(title="Fraud Detection Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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