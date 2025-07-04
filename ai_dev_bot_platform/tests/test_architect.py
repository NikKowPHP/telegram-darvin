# ROO-AUDIT-TAG :: feature-003-architectural-planning.md :: Implement architecture planning tests
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.api.endpoints.orchestrator import create_architecture_plan
from app.services.project_helpers import select_technology_stack
from app.agents.architect_agent import ArchitectAgent

@pytest.mark.asyncio
async def test_create_architecture_plan_success():
    # Mock dependencies
    mock_db = MagicMock()
    mock_user = MagicMock()
    
    # Mock ArchitectAgent
    mock_architect = AsyncMock()
    mock_architect.generate_initial_plan_and_docs.return_value = {
        "documentation": "Architecture docs",
        "tech_stack_suggestion": {"frontend": ["React"]},
        "todo_list_markdown": "- [ ] Task 1"
    }
    
    # Patch the ArchitectAgent
    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.api.endpoints.orchestrator.ArchitectAgent", lambda _: mock_architect)
        m.setattr("app.api.endpoints.orchestrator.LLMClient", MagicMock())
        
        response = await create_architecture_plan(
            {"title": "Test Project", "description": "Test requirements"},
            mock_db,
            mock_user
        )
        
    assert "architecture" in response
    assert "tech_stack" in response
    assert "todo_list" in response

@pytest.mark.asyncio
async def test_create_architecture_plan_error():
    mock_db = MagicMock()
    mock_user = MagicMock()
    
    mock_architect = AsyncMock()
    mock_architect.generate_initial_plan_and_docs.return_value = {
        "error": "Test error"
    }
    
    with pytest.MonkeyPatch.context() as m:
        m.setattr("app.api.endpoints.orchestrator.ArchitectAgent", lambda _: mock_architect)
        m.setattr("app.api.endpoints.orchestrator.LLMClient", MagicMock())
        
        with pytest.raises(HTTPException):
            await create_architecture_plan(
                {"title": "Test Project", "description": "Test requirements"},
                mock_db,
                mock_user
            )

def test_technology_stack_selection():
    # Test default stack
    stack = select_technology_stack("")
    assert len(stack["frontend"]) > 0
    assert len(stack["backend"]) > 0
    
    # Test Python backend selection
    stack = select_technology_stack("We want to use Python")
    assert "Python" in stack["backend"]
    
    # Test mobile frontend
    stack = select_technology_stack("Mobile app")
    assert "React Native" in stack["frontend"]
# ROO-AUDIT-TAG :: feature-003-architectural-planning.md :: END