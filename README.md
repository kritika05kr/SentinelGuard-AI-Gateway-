                          ┌───────────────────────┐
                          │      User Prompt      │
                          └───────────────────────┘
                                      │
                                      ▼
                  ┌──────────────────────────────────────────┐
                  │        SentinelGuard Safety Gateway       │
                  └──────────────────────────────────────────┘
                                      │
                                      ▼

──────────────────────────── 1) DETECTION LAYER ────────────────────────────
• Regex Detectors          → PII, emails, API keys, credentials
• Financial Detector        → salary, revenue, currency amounts
• Harmful Intent Detector   → hacking / violence override
• ML Classifier (LogReg)    → SAFE / SENSITIVE / POLICY_RISK / HARMFUL

──────────────────────────── 2) POLICY RAG LAYER ───────────────────────────
• Employee Handbook PDF → extracted & chunked
• TF-IDF vectorizer     → vector store
• Similarity search     → top policy matches
• Policy alignment score (0–1)

──────────────────────────── 3) RISK ENGINE ─────────────────────────────────
final_risk =
    0.7 * detector_risk
  + 0.1 * ml_risk
  + 0.2 * policy_alignment

──────────────────────────── 4) CONFIDENCE ENGINE ──────────────────────────
confidence =
    weighted ML confidence
  + detector agreement
  + policy match strength

──────────────────────────── 5) DECISION ENGINE ────────────────────────────
• ALLOW   → safe
• REDACT  → fixable sensitive info
• BLOCK   → unsafe / harmful

──────────────────────────── 6) SANITIZATION LAYER ─────────────────────────
• email      → [REDACTED_EMAIL]
• secret     → [REDACTED_SECRET]
• amounts    → [REDACTED_AMOUNT]

──────────────────────────── 7) OUTPUT TO LLM ──────────────────────────────
• Only sanitized prompt is forwarded
• Dummy LLM response shown in UI

                                      │
                                      ▼
                ┌──────────────────────────────────────────┐
                │                Frontend UI                │
                │ Chat + Safety Inspector + Compliance View │
                └──────────────────────────────────────────┘
