from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from typing import Optional, List
import uuid


class ProjectService:
    def create_project(
        self, db: Session, project_in: ProjectCreate, user_id: int
    ) -> Project:
        db_project = Project(
            user_id=user_id,  # Ensure user_id is passed correctly
            title=project_in.title,
            description=project_in.description,
            tech_stack=project_in.tech_stack,
            status="planning",  # Initial status after creation request
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project

    def get_project(self, db: Session, project_id: uuid.UUID) -> Optional[Project]:
        return db.query(Project).filter(Project.id == project_id).first()

    def get_projects_by_user(self, db: Session, user_id: int) -> List[Project]:
        return db.query(Project).filter(Project.user_id == user_id).all()

    def update_project(
        self, db: Session, project_id: uuid.UUID, project_upd: ProjectUpdate
    ) -> Optional[Project]:
        db_project = self.get_project(db, project_id)
        if db_project:
            update_data = project_upd.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_project, key, value)
            db.commit()
            db.refresh(db_project)
        return db_project
