import json
from pathlib import Path
from typing import List

from .audit_models import AuditLogEntry


BASE_DIR = Path(__file__).resolve().parents[2]  # .../backend
LOG_DIR = BASE_DIR / "data"
LOG_FILE = LOG_DIR / "audit_logs.jsonl"

LOG_DIR.mkdir(exist_ok=True)


def write_audit_log(entry: AuditLogEntry) -> None:
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(entry.model_dump_json() + "\n")


def read_audit_logs(limit: int = 50) -> List[AuditLogEntry]:
    if not LOG_FILE.exists():
        return []

    with LOG_FILE.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    # last N lines
    last_lines = lines[-limit:]
    entries: List[AuditLogEntry] = []
    for line in last_lines:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            entries.append(AuditLogEntry(**data))
        except Exception:
            # skip malformed line
            continue

    # newest first
    entries.reverse()
    return entries
