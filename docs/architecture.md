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
 
![System Architecture](/images/architecture_flow.png)

### Components
 
**My application**
- **Frontend (React)** — handles login, interview/company selection, interact/submit buttons, timer display
- **Backend (FastAPI)** — single orchestrator. All requests from frontend go here first; backend is the only thing that talks to external services and the DB
- **SER model (custom)** — your own speech emotion recognition model, called after each answer to score confidence/delivery
**External AI services** (called by backend, never directly by frontend)
- **LLM (Claude)** — decides what to ask, generates follow-ups, produces end-of-session feedback
- **TTS (ElevenLabs)** — converts question text to audio
- **STT (Whisper)** — transcribes user's spoken answer to text
**Storage**
- **Session DB (Postgres)** — session state, config
- **Question bank (Postgres)** — static reference data: company + interview type + question text
- **Answers table (Postgres)** — one row per question answered; this is the conversation history record
- **Audio storage (S3)** — raw audio per answer, auto-expires after retention period
### Answers table structure
 
This table is separate from raw audio storage — it holds the *record* of the conversation, not the audio file itself. It's what feeds both the LLM's context (for follow-up questions) and the end-of-session feedback generation.
 
| Field | Type | Purpose |
|---|---|---|
| `answer_id` | UUID (PK) | unique row identifier |
| `session_id` | UUID (FK) | links back to the session |
| `question_index` | int | which question this is within the session (0-indexed) |
| `question_text` | text | the question actually asked (post-LLM framing) |
| `answer_text` | text | transcribed answer from STT |
| `audio_ref` | text | pointer/key to the raw audio file in S3 |
| `ser_score` | json/float | emotion/confidence score from the SER model |
| `timestamp` | datetime | when this answer was submitted |
 
### Flow summary
1. Frontend sends interview type + company to backend on Start
2. Backend queries question bank for the first question, sends text to LLM for framing, sends result to TTS -> audio streamed back to frontend
3. User hits Interact (recording starts) -> Submit (recording stops, audio sent to backend)
4. Backend sends audio to STT -> transcribed text + question saved as a new row in the answers table -> audio sent to SER model (async) -> `ser_score` updated on that row -> conversation history (from answers table) sent to LLM for next question/follow-up
5. Loop continues until questions exhausted or timer hits the type's limit
6. On completion: LLM generates feedback from full answers table history + aggregated SER scores
### Key design decisions
- The backend is the **single point of contact** for the frontend — it fans out to LLM/TTS/STT/SER/DB internally. This keeps API keys server-side only and means the frontend never needs to know which third-party service is being used.
- The **answers table** is kept separate from raw audio storage — the DB holds the queryable conversation record (text + scores), while S3 holds the heavier binary audio files. This keeps the DB fast and lets audio expire independently without touching the conversation record.


## Data Flow
![Data flow diagram](./images/data-flow-diagram.png)

**v1 decisions:**
- Turn-based (record → submit), not real-time streaming
- Stateful conversation (LLM sees full history within a session)
- Exact-match question retrieval (company + type), not vector search
- Emotional/delivery feedback given at end of session, not per-turn