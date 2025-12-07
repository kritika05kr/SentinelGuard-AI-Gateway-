High-Level Architecture – SentinelGuard AI Gateway                   
                   ┌───────────────────────────────────┐
                   │             User Prompt            │
                   └───────────────────────────────────┘
                                   │
                                   ▼
        ┌─────────────────────────────────────────────────────────┐
        │              SentinelGuard Safety Gateway               │
        └─────────────────────────────────────────────────────────┘
                                   │
                                   ▼
────────────────────────────────────────────────────────────────────────
      1. Detection Layer (Rule-Based + ML + Heuristics)
────────────────────────────────────────────────────────────────────────
│  • Regex Detectors → PII, emails, API keys, credentials           │
│  • Financial Detector → salary, revenue, ₹ amounts                │
│  • Harmful Intent Detector → hacking/violence override            │
│  • ML Classifier (Logistic Regression) → SAFE / SENSITIVE / POLICY│
│                                                                     │
────────────────────────────────────────────────────────────────────────
      2. Policy RAG Layer
────────────────────────────────────────────────────────────────────────
│  • Handbook PDF → chunked & vectorized with TF-IDF               │
│  • Prompt similarity → relevant policy sections retrieved         │
│  • Policy alignment score computed                                │
│                                                                     │
────────────────────────────────────────────────────────────────────────
      3. Risk & Confidence Engine
────────────────────────────────────────────────────────────────────────
│  final_risk = 0.7*detectors + 0.1*ml + 0.2*policy                 │
│  confidence = weighted ML + detector agreement + policy match     │
│                                                                     │
────────────────────────────────────────────────────────────────────────
      4. Decision Engine
────────────────────────────────────────────────────────────────────────
│  • ALLOW (safe)                                                   │
│  • REDACT (fixable)                                               │
│  • BLOCK (unsafe / harmful)                                       │
│                                                                     │
────────────────────────────────────────────────────────────────────────
      5. Sanitization Layer
────────────────────────────────────────────────────────────────────────
│  • Redacts spans → [REDACTED_EMAIL], [REDACTED_SECRET], etc.      │
│                                                                     │
────────────────────────────────────────────────────────────────────────
      6. Output to LLM
────────────────────────────────────────────────────────────────────────
│  • Only sanitized prompt is forwarded                             │
│  • Dummy LLM response shown in UI                                 │
────────────────────────────────────────────────────────────────────────
                                   │
                                   ▼
        ┌─────────────────────────────────────────────────────────┐
        │                       Frontend UI                        │
        │   Chat Window + Safety Inspector + Ask Compliance        │
        └─────────────────────────────────────────────────────────┘
