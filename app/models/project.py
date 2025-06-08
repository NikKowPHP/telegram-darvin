import uuid
from sqlalchemy import Column, Integer, String, DateTime, JSON, TEXT, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False, default="Untitled Project")
    description = Column(TEXT, nullable=True)
    status = Column(String(50), default="gathering_requirements")
    tech_stack = Column(JSON, nullable=True)
    current_todo_markdown = Column(TEXT, nullable=True)
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User")