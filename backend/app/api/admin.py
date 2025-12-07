from fastapi import APIRouter, Query
from typing import List

from ..audit.audit_logger import read_audit_logs
from ..audit.audit_models import AuditLogEntry
from ..policy.policy_loader import load_policy_chunks
from ..models.schemas import PolicyReference


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/logs", response_model=list[AuditLogEntry])
def get_logs(limit: int = Query(50, ge=1, le=500)):
    """
    Return the last N audit log entries (newest first).
    """
    return read_audit_logs(limit=limit)


@router.get("/policies", response_model=list[PolicyReference])
def get_policies():
    """
    Return basic info about all policy chunks (for admin view).
    """
    chunks = load_policy_chunks()
    refs: List[PolicyReference] = []
    for i, ch in enumerate(chunks):
        refs.append(
            PolicyReference(
                id=str(ch.get("id", f"chunk-{i}")),
                section=str(ch.get("section", "?")),
                title=ch.get("title", "Policy"),
                snippet=ch.get("text", "")[:200] + "...",
            )
        )
    return refs
