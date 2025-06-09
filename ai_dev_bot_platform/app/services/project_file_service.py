from sqlalchemy.orm import Session
from app.models.project_file import ProjectFile
from app.schemas.project_file import ProjectFileCreate
from typing import List, Optional
import uuid

class ProjectFileService:
    def create_project_file(self, db: Session, project_id: uuid.UUID, file_path: str, content: str) -> ProjectFile:
        db_file = ProjectFile(
            project_id=project_id,
            file_path=file_path,
            content=content
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        return db_file

    def get_file(self, db: Session, file_id: uuid.UUID) -> Optional[ProjectFile]:
        return db.query(ProjectFile).filter(ProjectFile.id == file_id).first()

    def get_files_by_project(self, db: Session, project_id: uuid.UUID) -> List[ProjectFile]:
        return db.query(ProjectFile).filter(ProjectFile.project_id == project_id).all()

    def get_file_by_path(self, db: Session, project_id: uuid.UUID, file_path: str) -> Optional[ProjectFile]:
        return db.query(ProjectFile).filter(
            ProjectFile.project_id == project_id,
            ProjectFile.file_path == file_path
        ).first()

    def update_file_content(self, db: Session, file_id: uuid.UUID, new_content: str) -> Optional[ProjectFile]:
        db_file = self.get_file(db, file_id)
        if db_file:
            db_file.content = new_content
            db.commit()
            db.refresh(db_file)
        return db_file

    def delete_file(self, db: Session, file_id: uuid.UUID) -> bool:
        db_file = self.get_file(db, file_id)
        if db_file:
            db.delete(db_file)
            db.commit()
            return True
        return False