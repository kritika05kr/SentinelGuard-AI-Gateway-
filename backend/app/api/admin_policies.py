from fastapi import APIRouter, Query
from app.policy.rag_store import policy_rag_store

router = APIRouter(tags=["admin-policies"])


@router.get("/admin/policies/search")
def search_policies(q: str = Query(..., description="Search phrase")):
    """
    Simple RAG-based policy search.
    """
    res = policy_rag_store.find_policies(q, top_k=10)
    return {
        "query": q,
        "alignment_score": res["alignment_score"],
        "matches": res["matches"],
    }
