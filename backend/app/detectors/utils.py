import re
from typing import List
from ..models.schemas import Detection, DetectionType, SeverityLevel, TextSpan


EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(r"\b(?:\+?\d{1,3})?[ -]?\d{10}\b")


def find_spans(pattern: re.Pattern, text: str, dtype: DetectionType, severity: SeverityLevel) -> List[Detection]:
    detections: List[Detection] = []
    for match in pattern.finditer(text):
        span = TextSpan(start=match.start(), end=match.end(), text=match.group())
        detections.append(
            Detection(
                type=dtype,
                severity=severity,
                span=span,
                extra={}
            )
        )
    return detections
