import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix
import xgboost as xgb
import joblib
import os

# Load data
df = pd.read_csv('data/phishing_email.csv')

# Drop any empty rows just in case
df = df.dropna(subset=['text_combined', 'label'])

X_text = df['text_combined']
y = df['label']

# Split into train/test sets (80% train, 20% test)
X_train_text, X_test_text, y_train, y_test = train_test_split(
    X_text, y, test_size=0.2, random_state=42, stratify=y
)

# Convert email text into numeric features using TF-IDF
vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
X_train = vectorizer.fit_transform(X_train_text)
X_test = vectorizer.transform(X_test_text)

# Train XGBoost model
model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    eval_metric='logloss'
)
model.fit(X_train, y_train)

# Evaluate
preds = model.predict(X_test)
print("Classification Report:")
print(classification_report(y_test, preds))
print("Confusion Matrix:")
print(confusion_matrix(y_test, preds))

# Save the trained model and the vectorizer (we need both later)
os.makedirs('models', exist_ok=True)
joblib.dump(model, 'models/phishing_model.pkl')
joblib.dump(vectorizer, 'models/vectorizer.pkl')

print("\nModel and vectorizer saved to models/ folder")