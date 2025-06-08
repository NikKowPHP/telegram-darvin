from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import datetime

class ProjectBase(BaseModel):
    title: Optional[str] = "Untitled Project"
    description: Optional[str] = None
    tech_stack: Optional[Dict[str, Any]] = None

class ProjectCreate(ProjectBase):
    user_id: int # Must be provided by system

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