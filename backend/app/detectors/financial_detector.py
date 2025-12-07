import re
from typing import List
from ..models.schemas import Detection, DetectionType, SeverityLevel, TextSpan


CURRENCY_REGEX = re.compile(r"[₹$€]\s?\d+(?:[.,]\d+)*")


def detect_financial(text: str) -> List[Detection]:
    detections: List[Detection] = []
    for m in CURRENCY_REGEX.finditer(text):
        span = TextSpan(start=m.start(), end=m.end(), text=m.group())
        detections.append(
            Detection(
                type=DetectionType.FINANCIAL_DATA,
                severity=SeverityLevel.HIGH,
                span=span,
                extra={}
            )
        )
    return detections
