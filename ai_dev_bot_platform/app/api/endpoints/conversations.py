# ROO-AUDIT-TAG :: feature-001-requirement-gathering.md :: Implement POST /api/conversations endpoint
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List
from app.services.conversation_service import create_conversation
router = APIRouter()

class ConversationCreate(BaseModel):
    user_id: str
    initial_message: Optional[str] = None

class ConversationResponse(BaseModel):
    id: str
    user_id: str
    created_at: datetime
    messages: list[str]
    status: str

class ConversationListResponse(BaseModel):
    conversations: list[ConversationResponse]
    total: int
    page: int
    limit: int

@router.post(
    "/conversations",
    status_code=status.HTTP_201_CREATED,
    response_model=ConversationResponse,
    responses={
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error"}
    }
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
            created_at=conversation.created_at,
            messages=[conversation.initial_message] if conversation.initial_message else [],
            status="active"
        )
    except ValueError as e:
        logging.error(f"Invalid request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logging.error(f"Failed to create conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create conversation: {str(e)}"
        )

@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    responses={
        400: {"description": "Invalid request parameters"},
        404: {"description": "No conversations found"},
        500: {"description": "Internal server error"}
    }
)
async def get_conversations(
    user_id: Optional[str] = None,
    page: int = 1,
    limit: int = 10
):
    """Get paginated list of conversations with optional filtering"""
    from app.services.conversation_service import get_conversations
    
    try:
        conversations, total = await get_conversations(
            user_id=user_id,
            page=page,
            limit=limit
        )
        
        if not conversations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No conversations found"
            )
            
        return ConversationListResponse(
            conversations=[
                ConversationResponse(
                    id=str(conv.id),
                    user_id=conv.user_id,
                    created_at=conv.created_at,
                    messages=conv.messages,
                    status=conv.status
                ) for conv in conversations
            ],
            total=total,
            page=page,
            limit=limit
        )
        
    except ValueError as e:
        logging.error(f"Invalid request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logging.error(f"Failed to get conversations: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversations: {str(e)}"
        )
    # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: END
# ROO-AUDIT-TAG :: feature-001-requirement-gathering.md :: END