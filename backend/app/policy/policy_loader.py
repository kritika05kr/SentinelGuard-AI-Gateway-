import json
from pathlib import Path
from typing import List, Dict, Any

from ..core.config import settings


BASE_DIR = Path(__file__).resolve().parents[2]  # .../backend
POLICY_CHUNKS_PATH = BASE_DIR / settings.POLICY_CHUNKS_PATH


def load_policy_chunks() -> List[Dict[str, Any]]:
    if not POLICY_CHUNKS_PATH.exists():
        print(f"[POLICY] chunked_policies.json not found at {POLICY_CHUNKS_PATH}")
        return []

    with POLICY_CHUNKS_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("[POLICY] chunked_policies.json must contain a list")
        return []

    return data
