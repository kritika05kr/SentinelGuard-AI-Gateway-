from typing import List
from ..models.schemas import (
    Detection,
    ConfidenceAssessment,
    ConfidenceFactors,
)
from ..models.schemas import DetectionType


def compute_confidence(
    detections: List[Detection],
    policy_match_strength: float = 0.7,
    model_confidence_raw: float = 0.8,
) -> ConfidenceAssessment:
    """
    Phase 1: very simple calculation.
    - model_confidence_raw: pretend we have a model; fixed for now.
    - detector_agreement: how many unique detection types fired.
    - policy_alignment: use supplied policy_match_strength.
    """

    if detections:
        unique_types = {d.type for d in detections}
        detector_agreement = min(1.0, len(unique_types) / 4.0)  # assume 4 main detector families
    else:
        detector_agreement = 0.2  # low, since nothing fired

    model_confidence = model_confidence_raw
    policy_alignment = policy_match_strength

    # Weighted combination
    score_float = (
        0.4 * model_confidence
        + 0.3 * detector_agreement
        + 0.3 * policy_alignment
    )
    score = int(round(score_float * 100))

    factors = ConfidenceFactors(
        model_confidence=model_confidence,
        detector_agreement=detector_agreement,
        policy_alignment=policy_alignment,
    )

    return ConfidenceAssessment(score=score, factors=factors)
