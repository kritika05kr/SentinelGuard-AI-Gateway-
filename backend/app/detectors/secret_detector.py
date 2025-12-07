# backend/app/detectors/secret_detector.py

import re
from typing import List

from ..models.schemas import Detection, TextSpan


# Known provider-style secret patterns
SECRET_PATTERNS = [
    # Stripe live/test keys
    (re.compile(r"\bsk_(live|test)_[0-9a-zA-Z]{8,}\b"), "SECRET_API_KEY"),
    # AWS access key
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "SECRET_AWS_KEY"),
    # Generic long high-entropy token (24+ chars of base64-ish stuff)
    (re.compile(r"\b[a-zA-Z0-9_\-]{24,}\b"), "SECRET_TOKEN_LONG"),
]

# Key phrases that usually precede secrets
KEY_PHRASES = [
    "api key",
    "secret key",
    "access key",
]


def _make_span(start: int, end: int, text: str) -> TextSpan:
    return TextSpan(start=start, end=end, text=text[start:end])


def _detect_context_secrets(text: str) -> List[Detection]:
    detections: List[Detection] = []
    lower_text = text.lower()

    for phrase in KEY_PHRASES:
        # Find all positions of the phrase in the text (case-insensitive)
        for match in re.finditer(re.escape(phrase), lower_text):
            phrase_start = match.start()
            phrase_end = match.end()

            # Look ahead in a small window after the phrase
            # e.g. " is kk_123456", " : kk_123456", " kk_123456"
            window_start = phrase_end
            window_end = min(len(text), window_start + 100)
            window_text = text[window_start:window_end]

            # Find the first "token-like" sequence (letters/digits/_/-) of length ≥ 6
            token_match = re.search(r"([A-Za-z0-9_\-]{6,})", window_text)
            if not token_match:
                continue

            key_start = window_start + token_match.start()
            key_end = window_start + token_match.end()

            span = _make_span(key_start, key_end, text)
            detections.append(
                Detection(
                    type="SECRET_API_KEY",
                    severity="HIGH",
                    span=span,
                    details={
                        "pattern": "CONTEXT_API_KEY",
                        "phrase": phrase,
                    },
                )
            )

    return detections


def detect_secrets(text: str) -> List[Detection]:
    detections: List[Detection] = []

    # A) Context-based secrets like "api key is kk_123456"
    detections.extend(_detect_context_secrets(text))

    # B) Known provider-style secret formats anywhere in text
    for pattern, det_type in SECRET_PATTERNS:
        for m in pattern.finditer(text):
            span = _make_span(m.start(), m.end(), text)
            detections.append(
                Detection(
                    type=det_type,
                    severity="HIGH",
                    span=span,
                    details={"pattern": "KNOWN_PROVIDER"},
                )
            )

    # Deduplicate by (start, end, type)
    unique = {}
    for d in detections:
        key = (d.span.start, d.span.end, d.type)
        if key not in unique:
            unique[key] = d

    return list(unique.values())
