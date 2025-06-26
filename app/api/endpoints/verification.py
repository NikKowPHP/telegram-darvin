from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.services.verification_service import VerificationService
from app.services.project_service import ProjectService

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
    verification_service: VerificationService = Depends()
):
    """Verify code implementation against project requirements."""
    try:
        # Get project details
        project = project_service.get_project(request.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Perform verification using the VerificationService
        verification_result = verification_service.verify_implementation(
            request.code,
            project.requirements
        )
        
        return {
            "valid": verification_result['valid'],
            "issues": verification_result.get('issues', []),
            "report": verification_result.get('report')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))