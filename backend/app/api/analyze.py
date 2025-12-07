# backend/app/api/analyze.py

from typing import List, Dict

from fastapi import APIRouter

from ..models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    Detection,
    DetectionSummary,
    Decision,
    DecisionAction,
    RiskAssessment,
    ConfidenceAssessment,
    TextSpan,
)
from ..detectors.pii_detector import detect_pii
from ..detectors.secret_detector import detect_secrets
from ..detectors.financial_detector import detect_financial
from ..risk.risk_engine import compute_risk
from ..risk.confidence_engine import compute_confidence
from ..policy.rule_engine import evaluate_rules
from ..policy.rag_store import get_policy_matches
from ..sanitize.redact import apply_redactions
from ..audit.audit_logger import write_audit_log
from ..audit.audit_models import build_audit_entry
from ..ml.safety_classifier import safety_classifier


router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("", response_model=AnalyzeResponse)
def analyze_prompt(payload: AnalyzeRequest) -> AnalyzeResponse:
    text = payload.prompt

    # --- Safety classifier (LogReg + TF-IDF) ---
    clf_label, clf_prob = safety_classifier.classify(text)
    # clf_label ∈ {SAFE, SENSITIVE, POLICY_RISK, HARMFUL} or None

    # --- Simple harmful-intent keyword check (rule-based) ---
    lower_text = text.lower()
    harmful_keywords = [
        # hacking / cybercrime
        "hack ", " hacking", "hack into", "hack the system", "hack the server",
        "how to hack", "crack wifi", "crack password", "bruteforce", "brute force",
        "keylogger", "malware", "ransomware", "rootkit", "backdoor",
        "sql injection", "xss attack", "csrf attack", "ddos", "dos attack",
        "bypass login", "bypass authentication", "steal data", "steal credentials",
        "phishing email", "phishing attack",

        # physical harm / violence
        "kill someone", "kill him", "kill her", "how to kill",
        "murder someone", "commit murder", "stab someone",
        "shoot someone", "school shooting", "mass shooting",
        "plant a bomb", "make a bomb", "bomb attack",
        "terrorist attack", "join terrorist", "assassinate",
        "poison someone", "poison her", "poison him",
    ]
    harmful_intent_rule = any(k in lower_text for k in harmful_keywords)
    harmful_intent_model = clf_label == "HARMFUL" and clf_prob >= 0.7
    harmful_intent = harmful_intent_rule or harmful_intent_model

    # --- 1. Run detectors (PII, secrets, financial, etc.) ---
    detections: List[Detection] = []
    detections.extend(detect_pii(text))
    detections.extend(detect_secrets(text))
    detections.extend(detect_financial(text))
    # TODO: add more detectors later (legal, code, etc.)

    # detection counts per type
    counts: Dict[str, int] = {}
    for d in detections:
        counts[d.type] = counts.get(d.type, 0) + 1

    detection_summary = DetectionSummary(
        detections=detections,
        detection_counts=counts,
    )

    # collect highlight spans for UI
    highlight_spans: List[TextSpan] = [
        d.span for d in detections if d.span is not None
    ]

    # --- 2. Policy matches (RAG over handbook) ---
    policy_alignment_score, rag_policy_refs = get_policy_matches(text)

    # --- 3. Compute base risk from detectors ---
    risk: RiskAssessment = compute_risk(detections)

    # 3b. Boost risk using policy alignment (0..1 → up to +20)
    base_risk_score = risk.score
    boosted_score = min(100, base_risk_score + int(20 * policy_alignment_score))
    if boosted_score != base_risk_score:
        risk.score = boosted_score

    # 3c. Adjust risk based on safety classifier label
    if clf_label is not None:
        if clf_label == "HARMFUL":
            risk.score = max(risk.score, 100)
        elif clf_label == "POLICY_RISK":
            risk.score = max(risk.score, min(100, risk.score + 40))
        elif clf_label == "SENSITIVE":
            risk.score = max(risk.score, min(100, risk.score + 25))
        elif clf_label == "SAFE" and clf_prob > 0.8 and risk.score < 20:
            # Strong SAFE signal → keep risk low if detectors also low
            risk.score = min(risk.score, 15)

    # --- 4. Evaluate rules (action + rule-based policy refs) ---
    action, rule_policy_refs = evaluate_rules(detections, risk)

    # 4b. Hard safety override if harmful intent
    if harmful_intent:
        # force max risk
        risk.score = 100
        try:
            # If level is Enum
            risk.level = risk.level.__class__.HIGH
        except Exception:
            # Fallback string
            setattr(risk, "level", "HIGH")

        # force BLOCK
        action = DecisionAction.BLOCK

    # merge all policy refs
    policy_refs = rag_policy_refs + rule_policy_refs

    # --- 5. Compute confidence ---
    model_conf = clf_prob if clf_label is not None else 0.85
    confidence: ConfidenceAssessment = compute_confidence(
        detections,
        policy_match_strength=policy_alignment_score,
        model_confidence_raw=model_conf,
    )

    # If harmful intent detected, we are very sure
    if harmful_intent:
        try:
            confidence.score = max(confidence.score, 95)
            factors = getattr(confidence, "factors", None)
            if isinstance(factors, dict):
                factors["model_confidence"] = max(
                    factors.get("model_confidence", model_conf), 0.95
                )
                factors["detector_agreement"] = max(
                    factors.get("detector_agreement", 0.9), 0.95
                )
                factors["policy_alignment"] = max(
                    factors.get("policy_alignment", policy_alignment_score), 0.9
                )
        except Exception:
            pass

    # --- 6. Sanitization (redact sensitive spans) ---
    if action in (DecisionAction.REDACT, DecisionAction.BLOCK):
        sanitized_prompt = apply_redactions(text, detections)
    else:
        sanitized_prompt = text

    # If harmful intent, we don't want to send anything downstream
    if harmful_intent:
        sanitized_prompt = ""

    # --- 7. Build decision explanation ---
    harmful_note = (
        " Harmful or illegal intent detected and blocked."
        if harmful_intent
        else ""
    )
    clf_note = (
        f" Safety classifier: {clf_label} ({clf_prob:.2f})."
        if clf_label is not None
        else ""
    )
    risk_level_str = (
        risk.level.value if hasattr(risk.level, "value") else risk.level
    )

    decision_explanation = (
        f"Action: {action.value}. "
        f"Risk {risk.score} ({risk_level_str}). "
        f"Confidence {confidence.score}%. "
        f"Policy alignment {policy_alignment_score:.2f}."
        f"{harmful_note}{clf_note}"
    )

    decision = Decision(
        action=action,
        risk=risk,
        confidence=confidence,
        policy_refs=policy_refs,
        explanation=decision_explanation,
    )

    # --- 8. Safety timeline for UI ---
    timeline_steps = [
        "🔍 Analyzed your request for sensitive info.",
        f"🧠 Matched against {len(policy_refs)} relevant policies.",
        f"⚖️ Risk score: {risk.score} ({risk_level_str}).",
        f"✂️ Detected {len(detections)} potential sensitive items.",
    ]
    if clf_label is not None:
        timeline_steps.append(
            f"🤖 Safety classifier prediction: {clf_label} ({clf_prob:.2f})."
        )
    if harmful_intent:
        timeline_steps.append(
            "⚠️ Detected harmful or illegal intent (e.g., hacking or physical harm)."
        )
        timeline_steps.append(
            "🚫 Blocked the request without sending anything to downstream LLMs."
        )
    else:
        timeline_steps.append(
            f"🤖 Decision: {action.value}. Sanitized prompt prepared."
        )

    response = AnalyzeResponse(
        sanitized_prompt=sanitized_prompt,
        original_prompt=text,
        decision=decision,
        detection_summary=detection_summary,
        safety_timeline=timeline_steps,
        highlight_spans=highlight_spans,
    )

    # --- 9. Audit log (non-blocking) ---
    try:
        audit_entry = build_audit_entry(payload, response)
        write_audit_log(audit_entry)
    except Exception as e:
        print(f"[AUDIT] Failed to write log: {e}")

    return response
