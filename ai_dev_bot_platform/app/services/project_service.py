from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate
from typing import Optional, List
import uuid
import subprocess
import os
from app.agents.architect_agent import ArchitectAgent
from app.utils.llm_client import LLMClient
from app.core.config import settings
from pathlib import Path


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

    # ROO-AUDIT-TAG :: feature-005-iterative-implementation.md :: Add automatic code committing functionality
    def commit_code_changes(self, project: Project, generated_code: str, file_path: str) -> bool:
        """Commit generated code changes to the project repository."""
        try:
            # Ensure project directory exists
            project_dir = Path(settings.PROJECTS_DIR) / str(project.id)
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Write generated code to file
            full_path = project_dir / file_path
            with open(full_path, 'w') as f:
                f.write(generated_code)
                
            # Execute git commands
            subprocess.run(['git', 'add', str(full_path)], cwd=project_dir, check=True)
            subprocess.run(
                ['git', 'commit', '-m', f'feat: Auto-commit for project {project.id}\n\n{generated_code[:50]}...'],
                cwd=project_dir,
                check=True
            )
            return True
        except Exception as e:
            print(f"Error committing code changes: {str(e)}")
            return False
    # ROO-AUDIT-TAG :: feature-005-iterative-implementation.md :: END

    # ROO-AUDIT-TAG :: feature-005-iterative-implementation.md :: Add task status tracking methods
    def update_task_status(self, db: Session, project_id: uuid.UUID, task_id: str, status: str) -> Optional[Project]:
        """Update status for a specific task"""
        project = self.get_project(db, project_id)
        if project:
            statuses = project.task_statuses or {}
            statuses[task_id] = status
            project.task_statuses = statuses
            db.commit()
            db.refresh(project)
        return project

    def get_task_status(self, db: Session, project_id: uuid.UUID, task_id: str) -> Optional[str]:
        """Get status for a specific task"""
        project = self.get_project(db, project_id)
        if project and project.task_statuses:
            return project.task_statuses.get(task_id)
        return None

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
