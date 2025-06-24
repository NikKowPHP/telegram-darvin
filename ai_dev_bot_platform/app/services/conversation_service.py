from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.conversation_model import Conversation
from app.schemas.conversation import ConversationCreate, ConversationUpdate

class ConversationService:
    def __init__(self, db: Session):
        self.db = db

    async def create_conversation(self, conversation: ConversationCreate) -> Conversation:
        db_conversation = Conversation(**conversation.dict())
        self.db.add(db_conversation)
        self.db.commit()
        self.db.refresh(db_conversation)
        return db_conversation

    async def get_by_id(self, conversation_id: UUID) -> Optional[Conversation]:
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()

    async def get_by_user(self, user_id: UUID) -> List[Conversation]:
        return self.db.query(Conversation).filter(Conversation.user_id == user_id).all()

    async def update_conversation(
        self, conversation_id: UUID, conversation_update: ConversationUpdate
    ) -> Optional[Conversation]:
        db_conversation = await self.get_by_id(conversation_id)
        if db_conversation:
            for key, value in conversation_update.dict().items():
                setattr(db_conversation, key, value)
            self.db.commit()
            self.db.refresh(db_conversation)
        return db_conversation

    async def delete_conversation(self, conversation_id: UUID) -> bool:
        db_conversation = await self.get_by_id(conversation_id)
        if db_conversation:
            self.db.delete(db_conversation)
            self.db.commit()
            return True
        return False