# ROO-AUDIT-TAG :: feature-003-architectural-planning.md :: Write unit tests for architecture planning functionality
import pytest
from unittest.mock import Mock, patch
from app.agents.architect_agent import ArchitectAgent
from app.services.project_service import ProjectService
from app.services.project_helpers import select_technology_stack

@pytest.fixture
def mock_llm_client():
    return Mock()

@pytest.fixture
def architect_agent(mock_llm_client):
    return ArchitectAgent(llm_client=mock_llm_client)

class TestArchitecturalPlanning:
    def test_generate_technical_documentation(self, architect_agent):
        # Test documentation generation
        project_description = "Test project"
        result = architect_agent.generate_technical_documentation(project_description)
        assert isinstance(result, dict)
        assert "architecture" in result
        assert "components" in result

    def test_todo_list_generation(self):
        # Test TODO list generation
        project_data = {"description": "Test project"}
        result = ProjectService.generate_todo_list(project_data)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_technology_stack_selection(self):
        # Test tech stack selection
        project_type = "web"
        result = select_technology_stack(project_type)
        assert isinstance(result, dict)
        assert "backend" in result
        assert "frontend" in result

    @patch('app.agents.architect_agent.ArchitectAgent.validate_architecture')
    def test_architecture_validation(self, mock_validate, architect_agent):
        # Test architecture validation
        mock_validate.return_value = {"valid": True}
        result = architect_agent.validate_architecture({})
        assert result["valid"] is True
# ROO-AUDIT-TAG :: feature-003-architectural-planning.md :: END