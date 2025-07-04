# ROO-AUDIT-TAG :: feature-002-hierarchical-collaboration.md :: Implement API endpoint for task routing
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from app.schemas.user import User
from app.api.deps import get_db, get_current_active_user
from app.services.orchestrator_service import OrchestratorService

router = APIRouter()

@router.post("/orchestrate")
async def orchestrate_task(
    task_data: dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Route a task to the appropriate agent (Architect or Implementer)"""
    try:
        orchestrator = OrchestratorService(db)
        result = await orchestrator.process_user_request(current_user, task_data.get("description", ""))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ROO-AUDIT-TAG :: feature-002-hierarchical-collaboration.md :: END

# ROO-AUDIT-TAG :: feature-003-architectural-planning.md :: Implement architecture planning endpoint
@router.post("/plan")
async def create_architecture_plan(
    plan_request: dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Generate an architecture plan for a project"""
    try:
        from app.agents.architect_agent import ArchitectAgent
        from app.utils.llm_client import LLMClient
        
        llm_client = LLMClient()
        architect = ArchitectAgent(llm_client)
        
        response = await architect.generate_initial_plan_and_docs(
            project_requirements=plan_request.get("description", ""),
            project_title=plan_request.get("title", "New Project")
        )
        
        if "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
            
        return {
            "architecture": response.get("documentation", ""),
            "tech_stack": response.get("tech_stack_suggestion", {}),
            "todo_list": response.get("todo_list_markdown", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ROO-AUDIT-TAG :: feature-003-architectural-planning.md :: END

@router.post("/orchestrate/run-loop")
async def trigger_autonomous_loop(
    request_data: dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Trigger the autonomous development loop for a project"""
    try:
        project_id = request_data.get("project_id")
        if not project_id:
            raise HTTPException(
                status_code=400,
                detail="project_id is required"
            )

        orchestrator = OrchestratorService(db)
        result = await orchestrator.run_autonomous_loop(project_id)
        
        return {
            "status": "success",
            "project_id": project_id,
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run autonomous loop: {str(e)}"
        )