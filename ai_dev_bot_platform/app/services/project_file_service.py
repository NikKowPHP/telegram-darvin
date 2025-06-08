from sqlalchemy.orm import Session
from app.models.project_file import ProjectFile
from app.schemas.project_file import ProjectFileCreate, ProjectFileUpdate
from typing import Optional, List
import uuid

class ProjectFileService:
    def create_file(self, db: Session, project_id: uuid.UUID, file_path: str, content: str, file_type: Optional[str] = None) -> ProjectFile:
        db_file = ProjectFile(
            project_id=project_id,
            file_path=file_path,
            file_type=file_type,
            content=content
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        return db_file

    def get_file_by_path(self, db: Session, project_id: uuid.UUID, file_path: str) -> Optional[ProjectFile]:
        return db.query(ProjectFile).filter(
            ProjectFile.project_id == project_id,
            ProjectFile.file_path == file_path
        ).first()

    def get_files_by_project(self, db: Session, project_id: uuid.UUID) -> List[ProjectFile]:
        return db.query(ProjectFile).filter(ProjectFile.project_id == project_id).all()

    def update_file_content(self, db: Session, file_id: uuid.UUID, new_content: str) -> Optional[ProjectFile]:
        db_file = db.query(ProjectFile).filter(ProjectFile.id == file_id).first()
        if db_file:
            db_file.content = new_content
            db.commit()
            db.refresh(db_file)
        return db_file

    def delete_file(self, db: Session, file_id: uuid.UUID) -> bool:
        db_file = db.query(ProjectFile).filter(ProjectFile.id == file_id).first()
        if db_file:
            db.delete(db_file)
            db.commit()
            return True
        return False

project_file_service = ProjectFileService()