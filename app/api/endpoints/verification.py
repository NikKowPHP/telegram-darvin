# ROO-AUDIT-TAG :: feature-006-automated-verification.md :: Implement API endpoint for verification
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.services.project_service import ProjectService
from app.agents.architect_agent import ArchitectAgent
from app.services.codebase_indexing_service import CodebaseIndexingService
from app.utils.llm_client import LLMClient
from app.core.config import get_app_settings
settings = get_app_settings()

router = APIRouter()

class VerificationRequest(BaseModel):
    code: str
    project_id: str

class VerificationResponse(BaseModel):
    valid: bool
    issues: list[str]
    report: Optional[str]

@router.post("/verify", response_model=VerificationResponse)
async def verify_code(
    request: VerificationRequest,
    project_service: ProjectService = Depends(),
    llm_client: LLMClient = Depends(),
    index_service: CodebaseIndexingService = Depends()
):
    """Verify code implementation against project requirements."""
    # ROO-AUDIT-TAG :: feature-006-automated-verification.md :: API verification endpoint
    try:
        # Get project details
        project = project_service.get_project(request.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Initialize architect agent
        architect_agent = ArchitectAgent(llm_client, index_service)
        
        # Perform verification
        verification_result = architect_agent.verify_implementation(
            request.code,
            project.requirements,
            project.todo_list
        )
        
        # Generate report
        report = architect_agent.generate_verification_report(verification_result)
        
        return {
            "valid": verification_result['valid'],
            "issues": verification_result['issues'],
            "report": report
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ROO-AUDIT-TAG :: feature-006-automated-verification.md :: END