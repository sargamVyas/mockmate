## Current Scope (v1)

| Interview Type | Question Count | Time Limit |
|---|---|---|
| Behavioral | 5 questions | 30 min |
| Technical (LeetCode-style) | 1 easy + 1 medium | 40 min |
| System Design | 1 question | 40 min |

## Session State Machine
- Session-level states
- Question-level states
- Timeout handling


## Session Data

### Config (fixed once session starts)
| Field | Example |
|---|---|
| user_id | reference to user |
| interview_type | behavioral / technical / system_design |
| company (optional) | for question retrieval |
| question_count | 5 / 2 / 1 |
| time_limit_seconds | 1800 / 2400 / 2400 |
| session_id | unique ID |

### Dynamic (changes turn-by-turn)
| Field | Purpose |
|---|---|
| current_question_index | which question you're on |
| time_elapsed_seconds | for timeout check |
| conversation_history | list of {question, answer_text, timestamp} |
| current_state | session-level state |
| current_question_state | question-level state |
| audio_refs | pointers to stored audio per answer |

## Data Retention
- Raw audio auto-expires after [X days] — privacy + storage hygiene

## System Architecture


## Data Flow


**v1 decisions:**
- Turn-based (record → submit), not real-time streaming
- Stateful conversation (LLM sees full history within a session)
- Exact-match question retrieval (company + type), not vector search
- Emotional/delivery feedback given at end of session, not per-turn