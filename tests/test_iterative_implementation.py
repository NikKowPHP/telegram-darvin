# ROO-AUDIT-TAG :: feature-005-iterative-implementation.md :: Write integration tests for iterative implementation
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.project import Project
from app.services.project_service import ProjectService
from app.db.session import SessionLocal
import uuid

client = TestClient(app)

@pytest.fixture
def test_project():
    db = SessionLocal()
    project_service = ProjectService()
    project = project_service.create_project(
        db,
        ProjectCreate(
            title="Test Project",
            description="Test Description",
            tech_stack={"language": "python"}
        ),
        user_id=1
    )
    yield project
    db.delete(project)
    db.commit()
    db.close()

def test_task_execution_flow(test_project):
    # Test task execution API
    task_id = "test_task_1"
    response = client.post(
        "/api/execute",
        json={
            "project_id": str(test_project.id),
            "task_description": "Create test function",
            "task_id": task_id
        }
    )
    assert response.status_code == 201
    assert "result" in response.json()
    
    # Verify task status was updated
    db = SessionLocal()
    project_service = ProjectService()
    status = project_service.get_task_status(db, test_project.id, task_id)
    assert status == "complete"
    db.close()

def test_code_committing(test_project):
    # Test code committing functionality
    db = SessionLocal()
    project_service = ProjectService()
    
    # Simulate code generation
    test_code = "def test_func(): pass"
    file_path = "test_file.py"
    result = project_service.commit_code_changes(test_project, test_code, file_path)
    
    assert result is True
    # In real test, would verify file exists and git commit was made
    db.close()
# ROO-AUDIT-TAG :: feature-005-iterative-implementation.md :: END