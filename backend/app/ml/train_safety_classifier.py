# backend/app/ml/train_safety_classifier.py

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import joblib

# .../backend/app
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "ml" / "data"
MODEL_DIR = BASE_DIR / "ml" / "models"

DATA_PATH = DATA_DIR / "safety_prompts.csv"
MODEL_PATH = MODEL_DIR / "safety_classifier.joblib"


def load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"[SAFETY TRAIN] Dataset not found at {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    if "text" not in df.columns or "label" not in df.columns:
        raise ValueError("[SAFETY TRAIN] CSV must have 'text' and 'label' columns")
    return df


def train():
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data()
    X = df["text"].astype(str)
    y = df["label"].astype(str)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # TF-IDF + Logistic Regression pipeline
    clf = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    max_df=0.9,
                    min_df=1,
                    stop_words="english",
                ),
            ),
            (
                "logreg",
                LogisticRegression(
                    max_iter=200,
                    n_jobs=-1,
                    class_weight="balanced",
                ),
            ),
        ]
    )

    print("[SAFETY TRAIN] Training safety classifier...")
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[SAFETY TRAIN] Accuracy: {acc:.3f}")
    print("[SAFETY TRAIN] Classification report:")
    print(classification_report(y_test, y_pred))

    joblib.dump(clf, MODEL_PATH)
    print(f"[SAFETY TRAIN] Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    train()
