def generate_response(prompt: str) -> str:
    """
    Phase 1: no real LLM.
    Simply echo the prompt with a dummy message.
    Later, you can plug a local model here.
    """
    return f"[DUMMY LLM ANSWER] Based on your sanitized prompt: {prompt[:200]}..."
