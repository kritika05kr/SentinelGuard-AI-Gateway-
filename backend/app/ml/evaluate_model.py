import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

# Load your dataset (the one we created)
df = pd.read_csv(r"C:\Projects\SentinelGuard AI Gateway\backend\app\ml\data\safety_prompts.csv")


X = df["text"]
y = df["label"]

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Load vectorizer and model
tfidf = joblib.load("tfidf.pkl")
clf = joblib.load("safety_model.pkl")

# Transform test set
X_test_vec = tfidf.transform(X_test)

# Predict
preds = clf.predict(X_test_vec)

# Accuracy
acc = accuracy_score(y_test, preds)
print("Accuracy:", acc)

# Precision/Recall/F1
prec, rec, f1, _ = precision_recall_fscore_support(
    y_test, preds, average="weighted"
)
print("Precision:", prec)
print("Recall:", rec)
print("F1-score:", f1)

# Full report
print("\nClassification Report:\n")
print(classification_report(y_test, preds))
