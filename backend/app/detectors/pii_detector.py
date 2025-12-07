from typing import List
from .utils import EMAIL_REGEX, PHONE_REGEX, find_spans
from ..models.schemas import Detection, DetectionType, SeverityLevel


def detect_pii(text: str) -> List[Detection]:
    detections: List[Detection] = []
    # Emails
    detections.extend(find_spans(EMAIL_REGEX, text, DetectionType.PII_EMAIL, SeverityLevel.MEDIUM))
    # Phones
    detections.extend(find_spans(PHONE_REGEX, text, DetectionType.PII_PHONE, SeverityLevel.MEDIUM))
    return detections
