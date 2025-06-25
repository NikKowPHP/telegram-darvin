# ROO-AUDIT-TAG :: feature-001-requirement-gathering.md :: Create conversation_service
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from uuid import uuid4
from app.models.conversation_model import Conversation
from app.schemas.conversation import MessageBase  # Added import

class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    def start_conversation(self, user_id: str, project_id: Optional[str] = None) -> Conversation:
        """Create a new conversation in the database"""
        conversation = Conversation(
            id=str(uuid4()),
            user_id=user_id,
            project_id=project_id,
            messages=[]
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def add_message(self, conversation_id: str, message: Dict[str, Any]) -> Conversation:
        """Add a validated message to an existing conversation"""
        # Validate message structure
        validated_message = MessageBase(**message)  # This will raise ValidationError if invalid
        
        conversation = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        conversation.messages.append(validated_message.dict())
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Retrieve a conversation by its ID"""
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
# ROO-AUDIT-TAG :: feature-001-requirement-gathering.md :: END
