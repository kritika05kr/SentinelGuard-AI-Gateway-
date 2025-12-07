# backend/app/ml/safety_classifier.py

from pathlib import Path
from typing import Optional, Tuple

import joblib

# .../backend/app
BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "ml" / "models" / "safety_classifier.joblib"


class SafetyClassifier:
    """
    Wrapper around TF-IDF + Logistic Regression safety model.

    Labels expected:
      - SAFE
      - SENSITIVE
      - POLICY_RISK
      - HARMFUL
    """

    def __init__(self):
        self._model = None

    def load(self):
        if not MODEL_PATH.exists():
            print(f"[SAFETY CLASSIFIER] No model found at {MODEL_PATH}. Skipping load.")
            return
        self._model = joblib.load(MODEL_PATH)
        print(f"[SAFETY CLASSIFIER] Loaded model from {MODEL_PATH}")

    @property
    def is_ready(self) -> bool:
        return self._model is not None

    def classify(self, text: str) -> Tuple[Optional[str], float]:
        """
        Returns (label, probability_of_label).
        If model not loaded, returns (None, 0.0).
        """
        if not self.is_ready:
            return None, 0.0

        probs = self._model.predict_proba([text])[0]
        idx = probs.argmax()
        prob = float(probs[idx])
        label = self._model.classes_[idx]
        return label, prob


safety_classifier = SafetyClassifier()


def init_safety_classifier():
    """Call from app startup."""
    safety_classifier.load()
