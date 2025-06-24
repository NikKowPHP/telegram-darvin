from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class ConversationBase(BaseModel):
    user_id: UUID
    project_id: Optional[UUID] = None
    messages: dict


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(ConversationBase):
    pass


class ConversationInDB(ConversationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Conversation(ConversationInDB):
    pass
