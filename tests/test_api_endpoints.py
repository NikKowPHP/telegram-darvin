import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.project import ProjectCreate

client = TestClient(app)

def test_create_project():
    project_data = {
        "title": "Test Project",
        "description": "Test Description",
        "user_id": 1
    }
    response = client.post("/projects/", json=project_data)
    assert response.status_code == 200
    assert "id" in response.json()

def test_create_project_invalid_data():
    invalid_data = {"title": ""}
    response = client.post("/projects/", json=invalid_data)
    assert response.status_code == 422
    assert "detail" in response.json()

def test_refine_file():
    refine_data = {
        "file_path": "src/main.py",
        "project_id": "test-project",
        "instruction": "Add error handling"
    }
    response = client.post("/refine/", json=refine_data)
    assert response.status_code == 200
    assert "text" in response.json()