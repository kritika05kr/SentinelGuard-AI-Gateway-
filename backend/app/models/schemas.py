from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ---------- Basic span model ----------

class TextSpan(BaseModel):
    start: int
    end: int
    text: str


# ---------- Detection models ----------

class DetectionType(str, Enum):
    PII_EMAIL = "PII_EMAIL"
    PII_PHONE = "PII_PHONE"
    SECRET_API_KEY = "SECRET_API_KEY"
    SECRET_GENERIC = "SECRET_GENERIC"
    FINANCIAL_DATA = "FINANCIAL_DATA"
    LEGAL_CONTRACT = "LEGAL_CONTRACT"
    OTHER = "OTHER"


class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Detection(BaseModel):
    type: DetectionType
    severity: SeverityLevel
    span: Optional[TextSpan] = None
    extra: Dict[str, Any] = {}


# ---------- Policy models ----------

class PolicyReference(BaseModel):
    id: str
    section: str
    title: str
    snippet: str


# ---------- Risk & confidence ----------

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RiskAssessment(BaseModel):
    score: int = Field(ge=0, le=100)
    level: RiskLevel
    explanation: str


class ConfidenceFactors(BaseModel):
    model_confidence: float = Field(ge=0, le=1)
    detector_agreement: float = Field(ge=0, le=1)
    policy_alignment: float = Field(ge=0, le=1)


class ConfidenceAssessment(BaseModel):
    score: int = Field(ge=0, le=100)
    factors: ConfidenceFactors


# ---------- Decision models ----------

class DecisionAction(str, Enum):
    ALLOW = "ALLOW"
    REDACT = "REDACT"
    REWRITE = "REWRITE"
    BLOCK = "BLOCK"


class Decision(BaseModel):
    action: DecisionAction
    risk: RiskAssessment
    confidence: ConfidenceAssessment
    policy_refs: List[PolicyReference]
    explanation: str


# ---------- Analyze request/response ----------

class AnalyzeRequest(BaseModel):
    user_id: str
    role: Optional[str] = None
    prompt: str


class DetectionSummary(BaseModel):
    detections: List[Detection]
    detection_counts: Dict[DetectionType, int]


class AnalyzeResponse(BaseModel):
    sanitized_prompt: str
    original_prompt: str
    decision: Decision
    detection_summary: DetectionSummary
    # This is the "story" / timeline steps for UI
    safety_timeline: List[str]
    # For UI to highlight spans
    highlight_spans: List[TextSpan]


# ---------- Complete request/response ----------

class CompleteRequest(BaseModel):
    conversation_id: Optional[str] = None
    sanitized_prompt: str
    decision: Decision  # echo from previous analyze step (frontend passes it back)
    user_id: str


class CompleteResponse(BaseModel):
    answer: str
    outbound_decision: Optional[Decision] = None
