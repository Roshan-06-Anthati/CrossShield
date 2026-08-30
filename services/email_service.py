import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / 'models'

# Load once when this module is imported
model = joblib.load(MODEL_DIR / 'phishing_model.pkl')
vectorizer = joblib.load(MODEL_DIR / 'vectorizer.pkl')


def analyze_email_text(text: str) -> dict:
    features = vectorizer.transform([text])
    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0]

    is_phishing = bool(prediction == 1)
    risk_score = round(float(probability[1]) * 100, 2)

    return {
        "is_phishing": is_phishing,
        "risk_score": risk_score,
        "verdict": "Phishing" if is_phishing else "Legitimate"
    }