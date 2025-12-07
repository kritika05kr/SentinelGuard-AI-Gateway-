from fastapi import APIRouter
from ..models.schemas import CompleteRequest, CompleteResponse, Decision
from ..llm.local_llm import generate_response

router = APIRouter(prefix="/complete", tags=["complete"])


@router.post("", response_model=CompleteResponse)
def complete_chat(payload: CompleteRequest) -> CompleteResponse:
    """
    Phase 1:
    - Assume inbound prompt is already sanitized.
    - Call local LLM stub.
    - For now, we skip outbound scanning (can add later).
    """
    answer = generate_response(payload.sanitized_prompt)
    return CompleteResponse(answer=answer, outbound_decision=None)
