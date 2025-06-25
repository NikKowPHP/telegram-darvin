# ROO-AUDIT-TAG :: feature-001-requirement-gathering.md :: Add Conversation model
from sqlalchemy import Column, String, JSON
from app.db.base_class import Base

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    project_id = Column(String, index=True)
    messages = Column(JSON, default=list)
# ROO-AUDIT-TAG :: feature-001-requirement-gathering.md :: END
