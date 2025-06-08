from sqlalchemy.orm import Session
from app.models.project_file import ProjectFile
from app.schemas.project_file import ProjectFileCreate, ProjectFileUpdate
from typing import Optional, List
import uuid

def create_project_file(db: Session, project_file_in: ProjectFileCreate) -> ProjectFile:
    db_project_file = ProjectFile(
        project_id=project_file_in.project_id,
        file_path=project_file_in.file_path,
        file_type=project_file_in.file_type,
        content=project_file_in.content
    )
    db.add(db_project_file)
    db.commit()
    db.refresh(db_project_file)
    return db_project_file

def get_project_file_by_id(db: Session, file_id: uuid.UUID) -> Optional[ProjectFile]:
    return db.query(ProjectFile).filter(ProjectFile.id == file_id).first()

def get_project_files_by_project(db: Session, project_id: uuid.UUID) -> List[ProjectFile]:
    return db.query(ProjectFile).filter(ProjectFile.project_id == project_id).all()

def get_project_file_by_path(db: Session, project_id: uuid.UUID, file_path: str) -> Optional[ProjectFile]:
    return db.query(ProjectFile).filter(
        ProjectFile.project_id == project_id,
        ProjectFile.file_path == file_path
    ).first()

def update_project_file_content(db: Session, file_id: uuid.UUID, new_content: str) -> Optional[ProjectFile]:
    db_project_file = get_project_file_by_id(db, file_id)
    if db_project_file:
        db_project_file.content = new_content
        db.commit()
        db.refresh(db_project_file)
    return db_project_file

def delete_project_file(db: Session, file_id: uuid.UUID) -> bool:
    db_project_file = get_project_file_by_id(db, file_id)
    if db_project_file:
        db.delete(db_project_file)
        db.commit()
        return True
    return False