# backend/app/api/compliance.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..policy.rag_store import policy_rag_store  # ⬅ relative import


router = APIRouter(tags=["compliance"])


class AskComplianceRequest(BaseModel):
    user_id: str
    question: str


@router.post("/compliance/ask")
def ask_compliance(req: AskComplianceRequest):
    """
    Answer questions using ONLY policy text (no paid LLM).
    """
    if not policy_rag_store.is_ready:
        raise HTTPException(
            status_code=503,
            detail="Policy index is not loaded. Please rebuild policies or restart the service.",
        )

    try:
        res = policy_rag_store.find_policies(req.question, top_k=5)
    except Exception as e:
        # If RAG fails for any reason, don't crash the whole app
        raise HTTPException(status_code=500, detail=f"RAG error: {e}")

    matches = res["matches"]
    alignment = res["alignment_score"]

    if not matches:
        answer = (
            "I could not find any relevant policy clauses for your question in the "
            "current handbook index. Please contact HR / Compliance for clarification."
        )
        return {
            "answer": answer,
            "alignment_score": alignment,
            "policies": [],
        }

    bullet_lines = []
    for m in matches:
        bullet_lines.append(
            f"- Section {m['section']} – {m['title']}: {m['snippet']}"
        )

    answer = (
        "Based on the current handbook, the following policy sections are most relevant:\n\n"
        + "\n".join(bullet_lines)
        + "\n\nPlease treat these clauses as the primary guidance. "
          "For exceptions or special cases, contact HR / Compliance."
    )

    return {
        "answer": answer,
        "alignment_score": alignment,
        "policies": matches,
    }
