# ROO-AUDIT-TAG :: plan-001-requirement-gathering.md :: Implement validation for requirement inputs
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
import uuid
import datetime


class ProjectBase(BaseModel):
    # ROO-AUDIT-TAG :: plan-001-requirement-gathering.md :: Implement validation for requirement inputs
    title: str = Field(
        ..., min_length=3, max_length=100, description="Name of the project"
    )
    description: str = Field(
        ..., min_length=10, description="Detailed description of the project"
    )
    # ROO-AUDIT-TAG :: plan-001-requirement-gathering.md :: END
    tech_stack: Optional[Dict[str, Any]] = None


class ProjectCreate(ProjectBase):
    user_id: int  # Must be provided by system


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    tech_stack: Optional[Dict[str, Any]] = None
    current_todo_markdown: Optional[str] = None
    completed_at: Optional[datetime.datetime] = None


class ProjectInDBBase(ProjectBase):
    id: uuid.UUID
    user_id: int
    status: str
    current_todo_markdown: Optional[str] = None
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True


class Project(ProjectInDBBase):
    pass
