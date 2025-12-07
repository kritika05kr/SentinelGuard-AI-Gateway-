from typing import List
from ..models.schemas import Detection, DetectionType, TextSpan


REDACTION_MAP = {
    DetectionType.PII_EMAIL: "[REDACTED_EMAIL]",
    DetectionType.PII_PHONE: "[REDACTED_PHONE]",
    DetectionType.SECRET_API_KEY: "[REDACTED_SECRET]",
    DetectionType.SECRET_GENERIC: "[REDACTED_SECRET]",
    DetectionType.FINANCIAL_DATA: "[REDACTED_AMOUNT]",
}


def apply_redactions(text: str, detections: List[Detection]) -> str:
    """
    Apply redaction tokens to the text based on detection spans.
    For simplicity, we assume no overlapping spans.
    """

    # Sort by span start descending so indexes don't shift
    spans = [d.span for d in detections if d.span is not None]
    spans = sorted(spans, key=lambda s: s.start, reverse=True)

    redacted_text = text
    for span in spans:
        # Find matching detection type
        dtype = None
        for d in detections:
            if d.span == span:
                dtype = d.type
                break
        replacement = REDACTION_MAP.get(dtype, "[REDACTED]")
        redacted_text = (
            redacted_text[:span.start]
            + replacement
            + redacted_text[span.end:]
        )

    return redacted_text
