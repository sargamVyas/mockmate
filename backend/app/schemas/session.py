from pydantic import BaseModel
from enum import Enum
from typing import Optional
from uuid import UUID

class InterviewType(str, Enum):
    behavioral = "behavioral"
    technical = "technical"
    system_design = "system_design"


class SessionStartRequest(BaseModel):
    user_id:UUID
    interview_type: InterviewType
    company: Optional[str] = None

class SessionStartResponse(BaseModel):
    session_id: UUID
    session_status: str
    question_index: int
    question_text: str
    question_audio_url: str
    time_limit_seconds: int
    