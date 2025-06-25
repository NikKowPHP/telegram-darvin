# ROO-AUDIT-TAG :: feature-006-automated-verification.md :: Write integration tests for verification
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.agents.architect_agent import ArchitectAgent
from app.services.codebase_indexing_service import CodebaseIndexingService
from app.utils.llm_client import LLMClient

client = TestClient(app)

@pytest.fixture
def mock_llm_client():
    return LLMClient()

@pytest.fixture
def mock_index_service():
    return CodebaseIndexingService()

@pytest.fixture
def architect_agent(mock_llm_client, mock_index_service):
    return ArchitectAgent(mock_llm_client, mock_index_service)

def test_verification_endpoint():
    # ROO-AUDIT-TAG :: feature-006-automated-verification.md :: Test verification endpoint
    test_payload = {
        "code": "def test():\n    pass",
        "project_id": "test-project"
    }
    
    response = client.post("/api/verify", json=test_payload)
    assert response.status_code == 200
    assert "valid" in response.json()
    assert "issues" in response.json()
    assert "report" in response.json()

def test_architect_agent_verification(architect_agent):
    # ROO-AUDIT-TAG :: feature-006-automated-verification.md :: Test agent verification
    test_code = "def test():\n    pass"
    requirements = {"test_requirement": True}
    todo_list = ["test_todo"]
    
    result = architect_agent.verify_implementation(test_code, requirements, todo_list)
    assert isinstance(result, dict)
    assert "valid" in result
    assert "issues" in result
    assert "context" in result

def test_verification_report_generation(architect_agent):
    # ROO-AUDIT-TAG :: feature-006-automated-verification.md :: Test report generation
    verification_results = {
        "valid": True,
        "issues": [],
        "requirements": {"test": True},
        "todo_list": []
    }
    
    report = architect_agent.generate_verification_report(verification_results)
    assert isinstance(report, str)
    assert len(report) > 0

def test_verification_error_handling():
    # ROO-AUDIT-TAG :: feature-006-automated-verification.md :: Test error cases
    response = client.post("/api/verify", json={})
    assert response.status_code == 422
    
    response = client.post("/api/verify", json={"code": "test", "project_id": "nonexistent"})
    assert response.status_code == 404
# ROO-AUDIT-TAG :: feature-006-automated-verification.md :: END