from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from typing import Optional, List
import uuid
from app.agents.architect_agent import ArchitectAgent
from app.utils.llm_client import LLMClient
from app.core.config import settings


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

    # ROO-AUDIT-TAG :: feature-003-architectural-planning.md :: Implement generate_todo_list method
    async def generate_todo_list(self, project: Project) -> str:
        """Generate a TODO list for project implementation"""
        llm_client = LLMClient()
        architect_agent = ArchitectAgent(llm_client)
        
        # Get initial plan from architect agent
        plan = await architect_agent.generate_initial_plan_and_docs(
            project_requirements=project.description,
            project_title=project.title
        )
        
        if "error" in plan:
            return f"Error generating TODO list: {plan['error']}"
            
        return plan.get("todo_list_markdown", "No TODO list generated")
    # ROO-AUDIT-TAG :: feature-003-architectural-planning.md :: END

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
