from typing import List
from ..models.schemas import (
    Detection,
    RiskAssessment,
    RiskLevel,
)
from ..core.config import settings


def compute_risk(detections: List[Detection]) -> RiskAssessment:
    """
    Simple heuristic for Phase 1:
    - Each detection adds to risk score based on severity.
    - Clamped to [0, 100].
    """
    base_score = 0

    severity_weights = {
        "LOW": 5,
        "MEDIUM": 15,
        "HIGH": 30,
        "CRITICAL": 40,
    }

    for det in detections:
        w = severity_weights.get(det.severity.value, 10)
        base_score += w

    # Clamp
    base_score = max(0, min(100, base_score))

    # Map score to level using thresholds from config
    if base_score < settings.RISK_LOW_THRESHOLD:
        level = RiskLevel.LOW
    elif base_score < settings.RISK_HIGH_THRESHOLD:
        level = RiskLevel.MEDIUM
    else:
        level = RiskLevel.HIGH

    explanation = f"Computed risk score {base_score} based on {len(detections)} detections."

    return RiskAssessment(score=base_score, level=level, explanation=explanation)
