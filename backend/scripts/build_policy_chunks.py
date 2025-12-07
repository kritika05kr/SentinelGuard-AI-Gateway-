import re
import json
from pathlib import Path
from typing import List, Dict

from PyPDF2 import PdfReader  # free PDF library


BASE_DIR = Path(__file__).resolve().parents[1]  # .../backend
POLICIES_DIR = BASE_DIR / "policies"
SOURCE_DIR = POLICIES_DIR / "source"
OUTPUT_FILE = POLICIES_DIR / "chunked_policies.json"


def read_all_policy_texts() -> List[Dict]:
    """
    Read all .txt and .pdf files in policies/source and return list of
    {source_name, text} dicts.
    """
    docs = []
    if not SOURCE_DIR.exists():
        print(f"[POLICY BUILD] Source dir not found: {SOURCE_DIR}")
        return docs

    # .txt files
    for path in SOURCE_DIR.glob("*.txt"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        docs.append({"source_name": path.name, "text": text})
        print(f"[POLICY BUILD] Loaded TXT {path.name} ({len(text)} chars)")

    # .pdf files
    for path in SOURCE_DIR.glob("*.pdf"):
        reader = PdfReader(str(path))
        pages_text = []
        for page in reader.pages:
            try:
                pages_text.append(page.extract_text() or "")
            except Exception:
                continue
        text = "\n\n".join(pages_text)
        docs.append({"source_name": path.name, "text": text})
        print(f"[POLICY BUILD] Loaded PDF {path.name} ({len(text)} chars)")

    return docs


# Detect lines like: "5.11 Holidays", "Section 10.2 Workplace Violence", etc.
SECTION_RE = re.compile(
    r"^\s*(?:Section\s+)?(\d+(\.\d+)*)[\.\)]?\s+(.*)$",
    re.IGNORECASE,
)


def guess_category(para: str, section: str) -> str:
    """Very simple rule-based category classifier."""
    t = para.lower()

    # Security / confidentiality / social media etc.
    if any(k in t for k in [
        "information security",
        "proprietary information",
        "confidential information",
        "social media policy",
        "use of electronic communication",
        "email", "internet", "voicemail"
    ]):
        return "SECURITY_PRIVACY"

    # PII / harassment / equal opportunity
    if any(k in t for k in [
        "harassment", "discrimination", "equal employment",
        "protected", "sexual harassment"
    ]):
        return "FAIR_EMPLOYMENT"

    # Leave / holidays / attendance
    if any(k in t for k in [
        "paid time off", "leave", "holidays",
        "attendance", "maternity", "earned leaves"
    ]):
        return "LEAVE_POLICY"

    # Compensation / payroll
    if any(k in t for k in [
        "salary", "pay days", "ctc", "reimbursements",
        "payroll", "bonus"
    ]):
        return "COMPENSATION"

    # Behavior / conduct / ethics
    if any(k in t for k in [
        "employee behavior", "personal conduct",
        "ethical business practice", "professional appearance",
        "corrective action", "complaint resolution"
    ]):
        return "CONDUCT_ETHICS"

    # Safety / security / drugs / workplace violence
    if any(k in t for k in [
        "safety", "security", "drug and alcohol-free",
        "workplace violence", "fire evacuation",
        "accident reporting"
    ]):
        return "SAFETY_SECURITY"

    # Default fallback
    if section.startswith("11."):
        return "SOCIAL_MEDIA"
    if section.startswith("10."):
        return "SAFETY_SECURITY"

    return "GENERAL_HR"


def chunk_text_by_paragraphs(text: str, source_name: str) -> List[Dict]:
    """
    Chunk by paragraphs (split on double newlines).
    Try to detect section headers, assign section/title/category/weight.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: List[Dict] = []

    current_section = "?"
    current_title = f"From {source_name}"

    for idx, para in enumerate(paragraphs):
        first_line = para.splitlines()[0]
        m = SECTION_RE.match(first_line)
        if m:
            section = m.group(1).strip()
            title = m.group(3).strip() or f"Section {section}"
            current_section = section
            current_title = title

        category = guess_category(para, current_section)

        # Category-based weight: important sections get more influence
        base_weight = 1.0
        if category in ("SECURITY_PRIVACY", "SAFETY_SECURITY", "CONDUCT_ETHICS", "SOCIAL_MEDIA"):
            weight = 1.5
        else:
            weight = base_weight

        chunk_id = f"{source_name}-chunk-{idx}"

        chunks.append(
            {
                "id": chunk_id,
                "section": current_section,
                "title": current_title,
                "text": para,
                "source": source_name,
                "category": category,
                "weight": weight,
            }
        )

    return chunks


def build_chunks() -> List[Dict]:
    docs = read_all_policy_texts()
    all_chunks: List[Dict] = []

    for doc in docs:
        doc_chunks = chunk_text_by_paragraphs(doc["text"], doc["source_name"])
        all_chunks.extend(doc_chunks)

    print(f"[POLICY BUILD] Built {len(all_chunks)} chunks total.")
    return all_chunks


def main():
    POLICIES_DIR.mkdir(exist_ok=True)
    SOURCE_DIR.mkdir(exist_ok=True)

    chunks = build_chunks()

    # Filter out very tiny paragraphs
    filtered = [ch for ch in chunks if len(ch["text"]) > 80]
    print(f"[POLICY BUILD] Filtered to {len(filtered)} chunks (removed very short ones).")

    OUTPUT_FILE.write_text(
        json.dumps(filtered, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[POLICY BUILD] Wrote {len(filtered)} chunks to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
