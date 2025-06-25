# ROO-AUDIT-TAG :: feature-001-requirement-gathering.md :: Add input validation for conversation messages
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List, Dict, Any

class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    role: str = Field(..., regex="^(user|bot|system)$")
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    @validator('content')
    def content_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Message content cannot be empty")
        return v

class ConversationBase(BaseModel):
    user_id: str
    project_id: Optional[str] = None
    messages: List[MessageBase] = []

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: str
# ROO-AUDIT-TAG :: feature-001-requirement-gathering.md :: END
