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
───────────────────────────────────────────────────────────────────────────
1) DETECTION LAYER  (Rule-Based + ML + Heuristics)
───────────────────────────────────────────────────────────────────────────
• Regex Detectors          → PII, emails, API keys, credentials  
• Financial Detector        → salary, revenue, currency markers  
• Harmful Intent Detector   → hacking / violence override  
• ML Classifier (LogReg)    → SAFE / SENSITIVE / POLICY_RISK / HARMFUL  


───────────────────────────────────────────────────────────────────────────
2) POLICY RAG LAYER
───────────────────────────────────────────────────────────────────────────
• PDF Handbook → extracted & chunked  
• TF-IDF vectorizer → document retrieval  
• Similarity search → top policy sections  
• Policy alignment score (0–1)  


───────────────────────────────────────────────────────────────────────────
3) RISK & CONFIDENCE ENGINE
───────────────────────────────────────────────────────────────────────────
final_risk     = 0.7 * detector_risk  + 0.1 * ml_risk + 0.2 * policy_alignment  
confidence     = weighted ML + detector agreement + policy match  


───────────────────────────────────────────────────────────────────────────
4) DECISION ENGINE
───────────────────────────────────────────────────────────────────────────
• ALLOW     → safe  
• REDACT    → fixable sensitive info  
• BLOCK     → unsafe / harmful  


───────────────────────────────────────────────────────────────────────────
5) SANITIZATION LAYER
───────────────────────────────────────────────────────────────────────────
• Replaces spans:
    email      → [REDACTED_EMAIL]  
    secret     → [REDACTED_SECRET]  
    amounts    → [REDACTED_AMOUNT]  


───────────────────────────────────────────────────────────────────────────
6) OUTPUT TO LLM
───────────────────────────────────────────────────────────────────────────
• Only sanitized prompt forwarded  
• Dummy LLM response shown in UI  


                                      │
                                      ▼
                ┌──────────────────────────────────────────┐
                │                Frontend UI                │
                │ Chat Window + Safety Inspector + Compliance│
                └──────────────────────────────────────────┘
