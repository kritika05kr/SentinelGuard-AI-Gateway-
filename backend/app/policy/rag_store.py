from pathlib import Path
from typing import List, Dict, Any, Tuple

import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parents[2]  # .../backend
POLICY_FILE = BASE_DIR / "policies" / "chunked_policies.json"


class PolicyRAGStore:
    """
    TF-IDF based RAG store for policy / handbook chunks.

    This version is:
      - category-aware
      - query-intent aware
      - uses per-query keyword filters to avoid random matches
      - de-duplicates near-duplicate chunks from same section/title/category
    """

    def __init__(self):
        self._policies: List[Dict[str, Any]] = []
        self._vectorizer: TfidfVectorizer | None = None
        self._matrix = None

    def load(self):
        if not POLICY_FILE.exists():
            print(f"[POLICY RAG] No policy file found at {POLICY_FILE}")
            return

        data = json.loads(POLICY_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            print("[POLICY RAG] Policy JSON is not a list")
            return

        self._policies = data
        texts = [p["text"] for p in self._policies]

        self._vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_df=0.9,
            min_df=2,
            stop_words="english",
        )
        self._matrix = self._vectorizer.fit_transform(texts)

        print(f"[POLICY RAG] Loaded {len(self._policies)} chunks from {POLICY_FILE}")

    @property
    def is_ready(self) -> bool:
        return self._vectorizer is not None and self._matrix is not None

    # ---------- query → preferred categories + keyword filters ----------

    def _infer_categories_and_keywords(
        self, query: str
    ) -> Tuple[List[str], List[str]]:
        """
        Map query intent to:
          - preferred policy categories
          - required keywords that must appear in the policy text
        This keeps results relevant instead of random.
        """
        q = query.lower()
        categories: List[str] = []
        required_keywords: List[str] = []

        # Resume / portfolio / company projects / external sharing of work
        if any(
            k in q
            for k in [
                "resume",
                "cv",
                "portfolio",
                "company project",
                "project in resume",
                "upload project",
                "put project in",
                "show work in resume",
            ]
        ):
            categories.extend(["SECURITY_PRIVACY", "CONDUCT_ETHICS", "SOCIAL_MEDIA"])
            # focus on policies about confidentiality / external sharing
            required_keywords.extend(
                [
                    "confidential",
                    "proprietary",
                    "information security",
                    "social media",
                    "public",
                    "external",
                    "blog",
                    "website",
                    "internet",
                    "email",
                    "post",
                    "publish",
                    "share",
                    "disclose",
                ]
            )

        # Social media / online posting
        if any(
            k in q
            for k in [
                "social media",
                "linkedin",
                "facebook",
                "twitter",
                "instagram",
                "blog",
                "post on",
                "post to",
            ]
        ):
            categories.extend(["SOCIAL_MEDIA", "SECURITY_PRIVACY", "CONDUCT_ETHICS"])
            required_keywords.extend(
                [
                    "social media",
                    "blog",
                    "website",
                    "post",
                    "internet",
                    "external",
                    "public",
                    "email",
                ]
            )

        # Salary / compensation
        if any(k in q for k in ["salary", "ctc", "payroll", "pay day", "compensation", "bonus"]):
            categories.append("COMPENSATION")
            # we don't force extra keywords here; salary words are usually enough

        # Leave / holidays / time off
        if any(k in q for k in ["leave", "holiday", "vacation", "paid time off", "pto", "maternity"]):
            categories.append("LEAVE_POLICY")

        # Safety / security at workplace
        if any(k in q for k in ["safety", "accident", "violence", "security", "drug", "alcohol"]):
            categories.append("SAFETY_SECURITY")

        # Behaviour / ethics / conduct
        if any(
            k in q
            for k in ["behavior", "behaviour", "ethics", "code of conduct", "gift", "bribe", "conflict of interest"]
        ):
            categories.append("CONDUCT_ETHICS")

        # Remove duplicates but preserve order
        cat_seen = set()
        ordered_categories = []
        for c in categories:
            if c not in cat_seen:
                cat_seen.add(c)
                ordered_categories.append(c)

        kw_seen = set()
        ordered_keywords = []
        for w in required_keywords:
            if w not in kw_seen:
                kw_seen.add(w)
                ordered_keywords.append(w)

        return ordered_categories, ordered_keywords

    # ---------- similarity + scoring ----------

    def _similarities(self, query: str) -> List[Tuple[int, float]]:
        if not self.is_ready:
            return []

        q_vec = self._vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self._matrix)[0]

        weighted: List[Tuple[int, float]] = []
        for idx, sim in enumerate(sims):
            weight = float(self._policies[idx].get("weight", 1.0))
            weighted.append((idx, float(sim) * weight))

        weighted.sort(key=lambda x: x[1], reverse=True)
        return weighted

    def find_policies(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Return:
          - matches: list of policy chunks (max top_k), prioritized
          - alignment_score: aggregated score (0..1)
        """
        ranked = self._similarities(query)
        if not ranked:
            return {"matches": [], "alignment_score": 0.0}

        preferred_cats, required_keywords = self._infer_categories_and_keywords(query)
        required_keywords = [w.lower() for w in required_keywords]

        matches_preferred: List[Dict[str, Any]] = []
        matches_other: List[Dict[str, Any]] = []
        scores_for_alignment: List[float] = []

        seen_section_title = set()

        for idx, score in ranked:
            if score < min_score:
                continue

            p = self._policies[idx]
            section = p.get("section") or "?"
            title = p.get("title") or "Policy"
            category = p.get("category", "UNKNOWN")
            text_lower = p["text"].lower()

            # If we have required keywords for this query, enforce them
            if required_keywords:
                if not any(kw in text_lower for kw in required_keywords):
                    continue  # skip policies that don't talk about relevant concepts

            key = f"{section}|{title}|{category}"
            if key in seen_section_title:
                # avoid multiple near-identical chunks from same section/title/category
                continue
            seen_section_title.add(key)

            item = {
                "id": p.get("id", f"policy-{idx}"),
                "section": section,
                "title": title,
                "snippet": p["text"][:350],
                "category": category,
                "weight": p.get("weight", 1.0),
                "score": float(score),
            }

            if preferred_cats and category in preferred_cats:
                matches_preferred.append(item)
                scores_for_alignment.append(float(score))
            else:
                matches_other.append(item)
                scores_for_alignment.append(float(score))

            # Avoid scanning entire matrix; enough candidates
            if len(matches_preferred) + len(matches_other) >= top_k * 3:
                break

        # If we have preferred category matches, use them first
        ordered_matches: List[Dict[str, Any]] = []
        ordered_matches.extend(matches_preferred)

        # If not enough, fill with "other" that survived keyword filter
        if len(ordered_matches) < top_k:
            needed = top_k - len(ordered_matches)
            ordered_matches.extend(matches_other[:needed])

        # Trim to top_k
        ordered_matches = ordered_matches[:top_k]

        if not ordered_matches:
            return {"matches": [], "alignment_score": 0.0}

        # Alignment score based on matches actually returned
        score_vals = [m["score"] for m in ordered_matches]
        max_possible = max(score_vals)
        avg = sum(score_vals) / len(score_vals) if score_vals else 0.0
        alignment = min(avg / max_possible, 1.0) if max_possible > 0 else 0.0

        return {
            "matches": ordered_matches,
            "alignment_score": alignment,
        }


# Singleton + helper for other modules

policy_rag_store = PolicyRAGStore()


def init_policy_rag():
    """Called from app.main startup event."""
    policy_rag_store.load()


def get_policy_matches(query: str, top_k: int = 5) -> Tuple[float, List[Dict[str, Any]]]:
    """
    Backwards-compatible helper for analyze.py and compliance.py.

    Returns: (policy_alignment_score, policy_refs_list)
    """
    res = policy_rag_store.find_policies(query, top_k=top_k)
    return res["alignment_score"], res["matches"]
