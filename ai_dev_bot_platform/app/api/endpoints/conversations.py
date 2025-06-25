# ROO-AUDIT-TAG :: feature-001-requirement-gathering.md :: Implement POST /api/conversations endpoint
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ConversationCreate(BaseModel):
    user_id: str
    initial_message: Optional[str] = None

@router.post("/conversations", status_code=status.HTTP_201_CREATED)
# ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: Implement conversation endpoint
async def create_conversation(data: ConversationCreate):
    """Create a new conversation for requirement gathering"""
    # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: Implement database replacement
    from app.services.conversation_service import create_conversation
    conversation = await create_conversation(
        user_id=data.user_id,
        initial_message=data.initial_message
    )
    # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: END
    return {
        "id": str(conversation.id),
        "user_id": conversation.user_id,
        "messages": [conversation.initial_message] if conversation.initial_message else []
    }
    # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: END
# ROO-AUDIT-TAG :: feature-001-requirement-gathering.md :: END