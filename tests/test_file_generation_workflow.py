import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.project import ProjectCreate
import os
import subprocess

client = TestClient(app)

@pytest.fixture
def test_project():
    return {
        "title": "Test Workflow Project",
        "description": "Testing file generation workflow"
    }

def test_file_generation_workflow(test_project):
    # Create project
    response = client.post("/projects/", json=test_project)
    assert response.status_code == 200
    project_id = response.json()["id"]
    
    # Add implementation task
    task = {"description": "Create src/main.py with hello world"}
    response = client.post(f"/projects/{project_id}/tasks", json=task)
    assert response.status_code == 200
    
    # Run implementation
    response = client.post(f"/projects/{project_id}/implement")
    assert response.status_code == 200
    
    # Verify file was created
    assert os.path.exists(f"projects/{project_id}/src/main.py")
    with open(f"projects/{project_id}/src/main.py") as f:
        content = f.read()
        assert "hello world" in content.lower()
    
    # Verify git commit
    result = subprocess.run(
        ["git", "log", "--oneline"],
        cwd=f"projects/{project_id}",
        capture_output=True,
        text=True
    )
    assert "Create src/main.py with hello world" in result.stdout

def test_file_generation_error_handling(test_project):
    # Test with invalid project ID
    response = client.post("/projects/invalid-id/implement")
    assert response.status_code == 404
    assert "Project not found" in response.json()["detail"]