import uuid
from sqlalchemy import Column, TEXT, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ai_dev_bot_platform.app.db.session import Base

class ProjectFile(Base):
    __tablename__ = "project_files"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    file_path = Column(String(1000), nullable=False)  # e.g., "src/main.py"
    file_type = Column(String(100), nullable=True)  # e.g., "python", "markdown"
    content = Column(TEXT, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    project = relationship("Project")