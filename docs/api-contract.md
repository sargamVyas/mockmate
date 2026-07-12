## API Contract

Base URL: `/api/v1`

---

### 1. Start a session

`POST /session/start`

**Request**
```json
{
  "user_id": "uuid",
  "interview_type": "behavioral | technical | system_design",
  "company": "string (optional)"
}
```

**Response `200`**
```json
{
  "session_id": "uuid",
  "session_status": "in_progress",
  "question_index": 0,
  "question_text": "string",
  "question_audio_url": "string (TTS output)",
  "time_limit_seconds": 1800
}
```

**Response `400`**
```json
{ "error": "invalid_interview_type" | "invalid_user" }
```

---

### 2. Interact (start recording)

`POST /session/{session_id}/interact`

**Request** — empty body, just marks question-level state as `recording`

**Response `200`**
```json
{
  "session_id": "uuid",
  "question_status": "recording"
}
```

**Response `409`**
```json
{ "error": "session_not_in_progress" | "session_expired" }
```

---

### 3. Submit an answer

`POST /session/{session_id}/submit`

**Request** — `multipart/form-data`
```
audio_file: binary
```

**Response `200`** (more questions remain)
```json
{
  "session_id": "uuid",
  "session_status": "in_progress",
  "question_index": 1,
  "answer_text": "string (transcribed, for debugging/display)",
  "next_question_text": "string",
  "next_question_audio_url": "string",
  "time_elapsed_seconds": 145
}
```

**Response `200`** (session just completed)
```json
{
  "session_id": "uuid",
  "session_status": "completed",
  "question_index": null,
  "next_question_text": null,
  "next_question_audio_url": null
}
```

**Response `400`**
```json
{ "error": "invalid_audio" | "transcription_failed" }
```

**Response `409`**
```json
{ "error": "session_already_completed" | "session_expired" }
```

---

### 4. Get session status

`GET /session/{session_id}/status`

**Response `200`**
```json
{
  "session_id": "uuid",
  "session_status": "not_started | in_progress | completed",
  "question_index": 2,
  "time_elapsed_seconds": 600,
  "time_limit_seconds": 1800
}
```

**Response `404`**
```json
{ "error": "session_not_found" }
```

---

### 5. Get final feedback (only valid once completed)

`GET /session/{session_id}/feedback`

**Response `200`**
```json
{
  "session_id": "uuid",
  "overall_feedback": "string (LLM-generated)",
  "content_score": "number or breakdown object",
  "delivery_feedback": "string (from aggregated SER scores)",
  "answers": [
    {
      "question_index": 0,
      "question_text": "string",
      "answer_text": "string",
      "ser_score": "float or json"
    }
  ]
}
```

**Response `409`**
```json
{ "error": "session_not_completed" }
```

---

### Conventions used throughout
- Every response includes `session_id` and, where relevant, `session_status` — so the frontend can always sync state
- Errors always return `{ "error": "snake_case_code" }` — consistent shape, easy to switch on in frontend
- Audio always travels as `multipart/form-data` on the way in, and as a `_url` (pointing to generated TTS audio) on the way out — never raw bytes in JSON
- `time_elapsed_seconds` is returned wherever relevant so frontend timer stays in sync with backend truth (don't trust a client-side-only timer)
