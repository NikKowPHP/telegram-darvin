from pydantic import BaseModel
from typing import Optional
import uuid
import datetime

class ProjectFileBase(BaseModel):
    file_path: str
    content: str
    file_type: Optional[str] = None

class ProjectFileCreate(ProjectFileBase):
    project_id: uuid.UUID

class ProjectFileUpdate(BaseModel):
    content: Optional[str] = None
    file_path: Optional[str] = None

class ProjectFileInDBBase(ProjectFileBase):
    id: uuid.UUID
    project_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class ProjectFile(ProjectFileInDBBase):
    pass