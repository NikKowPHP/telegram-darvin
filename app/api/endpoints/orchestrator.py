# ROO-AUDIT-TAG :: feature-005-iterative-implementation.md :: Implement API endpoint for task execution
from fastapi import APIRouter, HTTPException, status
from typing import Optional
import uuid
from app.agents.implementer_agent import ImplementerAgent
from app.agents.architect_agent import ArchitectAgent
from app.services.project_service import ProjectService
from app.utils.llm_client import LLMClient
from app.db.session import SessionLocal

router = APIRouter()

@router.post("/execute", status_code=status.HTTP_201_CREATED)
async def execute_task(
    project_id: uuid.UUID,
    task_description: str,
    task_id: Optional[str] = None
):
    # ROO-AUDIT-TAG :: feature-005-iterative-implementation.md :: Task execution endpoint logic
    db = SessionLocal()
    try:
        # Initialize services
        llm_client = LLMClient()
        implementer = ImplementerAgent(llm_client)
        project_service = ProjectService()
        
        # Update task status to in-progress
        if task_id:
            project_service.update_task_status(db, project_id, task_id, "in-progress")
        
        # Execute the task
        result = implementer.execute_task(task_description)
        
        # Update task status based on result
        if task_id:
            new_status = "complete" if result['status'] == 'complete' else "failed"
            project_service.update_task_status(db, project_id, task_id, new_status)
        
        return {
            "project_id": project_id,
            "task_id": task_id,
            "result": result
        }
    except Exception as e:
        if task_id:
            project_service.update_task_status(db, project_id, task_id, "failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task execution failed: {str(e)}"
        )
    finally:
        db.close()
# ROO-AUDIT-TAG :: feature-007-readme-generation.md :: Implement API endpoint for README generation
@router.post("/generate-readme", status_code=status.HTTP_200_OK)
async def generate_readme(project_details: dict):
    """Generate a README file based on project details."""
    db = SessionLocal()
    try:
        # Initialize services
        llm_client = LLMClient()
        architect = ArchitectAgent(llm_client)
        
        # Generate the README content
        readme_content = architect.generate_readme(project_details)
        
        return {
            "readme": readme_content,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"README generation failed: {str(e)}"
        )
    finally:
        db.close()
# ROO-AUDIT-TAG :: feature-007-readme-generation.md :: END

# ROO-AUDIT-TAG :: feature-005-iterative-implementation.md :: END