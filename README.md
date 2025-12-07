                          ┌───────────────────────┐
                          │      User Prompt      │
                          └───────────────────────┘
                                      │
                                      ▼
                  ┌──────────────────────────────────────────┐
                  │        SentinelGuard Safety Gateway       │
                  │              (Full Pipeline)              │
                  └──────────────────────────────────────────┘
                                      │
                                      ▼
                  ┌──────────────────────────────────────────┐
                  │                PIPELINE FLOW              │
                  │──────────────────────────────────────────│
                  │ 1) DETECTION LAYER                        │
                  │    • Regex → emails, PII, API keys        │
                  │    • Financial → revenue, salary, ₹       │
                  │    • Harmful Intent → hacking/violence    │
                  │    • ML Classifier → LogReg (4 classes)   │
                  │                                            │
                  │ 2) POLICY RAG LAYER                       │
                  │    • Handbook → chunked + TF-IDF vectors  │
                  │    • Similarity search → top policies     │
                  │    • Policy alignment score (0–1)         │
                  │                                            │
                  │ 3) RISK ENGINE                            │
                  │    final_risk =                           │
                  │        0.7 * detector_risk                │
                  │      + 0.1 * ml_risk                      │
                  │      + 0.2 * policy_alignment             │
                  │                                            │
                  │ 4) CONFIDENCE ENGINE                      │
                  │    confidence = ML + detectors + RAG      │
                  │                                            │
                  │ 5) DECISION ENGINE                        │
                  │    • ALLOW                                │
                  │    • REDACT                               │
                  │    • BLOCK                                │
                  │                                            │
                  │ 6) SANITIZATION LAYER                     │
                  │    • email → [REDACTED_EMAIL]             │
                  │    • secret → [REDACTED_SECRET]           │
                  │    • amount → [REDACTED_AMOUNT]           │
                  │                                            │
                  │ 7) OUTPUT TO LLM                          │
                  │    • Only sanitized text forwarded         │
                  └──────────────────────────────────────────┘
                                      │
                                      ▼
                ┌──────────────────────────────────────────┐
                │                Frontend UI                │
                │ Chat Window + Safety Inspector + RAG View │
                └──────────────────────────────────────────┘
