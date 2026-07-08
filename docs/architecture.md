## Current Scope (v1)

| Interview Type | Question Count | Time Limit |
|---|---|---|
| Behavioral | 5 questions | 30 min |
| Technical (LeetCode-style) | 1 easy + 1 medium | 40 min |
| System Design | 1 question | 40 min |

**v1 decisions:**
- Turn-based (record → submit), not real-time streaming
- Stateful conversation (LLM sees full history within a session)
- Exact-match question retrieval (company + type), not vector search
- Emotional/delivery feedback given at end of session, not per-turn