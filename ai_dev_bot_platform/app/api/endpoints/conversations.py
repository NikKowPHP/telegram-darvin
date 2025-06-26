# ROO-AUDIT-TAG :: feature-001-requirement-gathering.md :: Implement POST /api/conversations endpoint
import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from app.services.conversation_service import create_conversation
router = APIRouter()

class ConversationCreate(BaseModel):
    user_id: str
    initial_message: Optional[str] = None

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    messages: list[str]

@router.post(
    "/conversations",
    status_code=status.HTTP_201_CREATED,
    response_model=ConversationResponse
)
# ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: Implement conversation endpoint
async def create_conversation(data: ConversationCreate):
    """Create a new conversation for requirement gathering
    
    Args:
        data: ConversationCreate - contains user_id and optional initial_message
        
    Returns:
        ConversationResponse with conversation details
    """
    # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: Implement database replacement
    try:
        conversation = await create_conversation(
            user_id=data.user_id,
            initial_message=data.initial_message
        )
        return ConversationResponse(
            id=str(conversation.id),
            user_id=conversation.user_id,
            messages=[conversation.initial_message] if conversation.initial_message else []
        )
    except Exception as e:
        logging.error(f"Failed to create conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation"
        )
    # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: END
# ROO-AUDIT-TAG :: feature-001-requirement-gathering.md :: END