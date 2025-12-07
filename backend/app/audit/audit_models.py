from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel

from ..models.schemas import AnalyzeRequest, AnalyzeResponse


class AuditLogEntry(BaseModel):
    timestamp: datetime
    user_id: str
    role: str | None
    original_prompt: str
    sanitized_prompt: str
    decision: Dict[str, Any]
    detection_summary: Dict[str, Any]
    safety_timeline: list[str]


def build_audit_entry(req: AnalyzeRequest, res: AnalyzeResponse) -> AuditLogEntry:
    return AuditLogEntry(
        timestamp=datetime.utcnow(),
        user_id=req.user_id,
        role=req.role,
        original_prompt=res.original_prompt,
        sanitized_prompt=res.sanitized_prompt,
        decision=res.decision.model_dump(),
        detection_summary=res.detection_summary.model_dump(),
        safety_timeline=res.safety_timeline,
    )
