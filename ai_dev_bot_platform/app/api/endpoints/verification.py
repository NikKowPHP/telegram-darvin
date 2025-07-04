from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.session import get_db
from app.agents.architect_agent import ArchitectAgent
from app.services.verification_service import VerificationService

router = APIRouter()

@router.post("/verify", response_model=Dict[str, Any])
async def verify_implementation(
    request_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    Verify a code implementation against project requirements.
    Expects:
    - code_snippet: The code to verify
    - project_context: Context about the project
    - task_description: Description of what the code should do
    """
    try:
        # Get required data from request
        code_snippet = request_data.get("code_snippet")
        project_context = request_data.get("project_context")
        task_description = request_data.get("task_description")
        
        if not all([code_snippet, project_context, task_description]):
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: code_snippet, project_context, or task_description"
            )

        # Initialize services
        verification_service = VerificationService()
        architect_agent = ArchitectAgent()

        # Verify implementation
        result = await architect_agent.verify_implementation_step(
            code_snippet=code_snippet,
            project_context=project_context,
            task_description=task_description
        )

        return JSONResponse(content=result, status_code=200)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Verification failed: {str(e)}"
        )