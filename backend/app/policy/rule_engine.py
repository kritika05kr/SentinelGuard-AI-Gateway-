from typing import List, Tuple
from ..models.schemas import (
    Detection,
    DetectionType,
    DecisionAction,
    PolicyReference,
)
from ..models.schemas import RiskAssessment


def evaluate_rules(detections: List[Detection], risk: RiskAssessment) -> Tuple[DecisionAction, List[PolicyReference]]:
    """
    Phase 1: rule-of-thumb logic.
    Later, we will integrate real RAG-based policy lookup.
    """

    has_secret = any(d.type in (DetectionType.SECRET_API_KEY, DetectionType.SECRET_GENERIC) for d in detections)
    has_pii = any(d.type in (DetectionType.PII_EMAIL, DetectionType.PII_PHONE) for d in detections)
    has_financial = any(d.type == DetectionType.FINANCIAL_DATA for d in detections)

    policy_refs: List[PolicyReference] = []

    if has_secret:
        policy_refs.append(
            PolicyReference(
                id="policy-4.3",
                section="4.3",
                title="Source Code & Secrets",
                snippet="Secrets (passwords, API keys, certificates) must never be shared with external tools."
            )
        )

    if has_pii:
        policy_refs.append(
            PolicyReference(
                id="policy-5.1",
                section="5.1",
                title="PII Handling",
                snippet="Email IDs and phone numbers are considered personal data and must be protected."
            )
        )

    if has_financial:
        policy_refs.append(
            PolicyReference(
                id="policy-6.2",
                section="6.2",
                title="Financial Data Confidentiality",
                snippet="Internal financial figures may not be shared with unapproved external services."
            )
        )

    # Decide action
    if has_secret:
        # Very strict: BLOCK for now
        action = DecisionAction.BLOCK
    elif risk.level.name == "HIGH":
        action = DecisionAction.REDACT
    elif has_pii or has_financial:
        action = DecisionAction.REDACT
    else:
        action = DecisionAction.ALLOW

    return action, policy_refs
