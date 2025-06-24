# ROO-AUDIT-TAG :: refactoring-epic-002-persistent-indexing.md :: Create ProjectEmbedding model for pgvector
import uuid
from sqlalchemy import Column, TEXT, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from app.db.session import Base


class ProjectEmbedding(Base):
    __tablename__ = "project_embeddings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False, index=True
    )
    file_path = Column(String(1000), nullable=False)
    content_chunk = Column(TEXT, nullable=False)
    embedding = Column(Vector(384))  # Dimension for all-MiniLM-L6-v2 is 384


# ROO-AUDIT-TAG :: refactoring-epic-002-persistent-indexing.md :: END
