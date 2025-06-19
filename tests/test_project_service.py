import pytest
from sqlalchemy.orm import Session
from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.models.project import Project
from fastapi import HTTPException

@pytest.fixture
def project_service(db_session: Session):
    return ProjectService()

def test_create_project_invalid_data(project_service):
    invalid_project = ProjectCreate(title="", description="Test")
    with pytest.raises(HTTPException) as exc_info:
        project_service.create_project(None, invalid_project, user_id=1)
    assert exc_info.value.status_code == 400
    assert "Title cannot be empty" in exc_info.value.detail

def test_get_project_not_found(project_service, db_session: Session):
    with pytest.raises(HTTPException) as exc_info:
        project_service.get_project(db_session, project_id=999)
    assert exc_info.value.status_code == 404
    assert "Project not found" in exc_info.value.detail

def test_update_project_invalid_id(project_service, db_session: Session):
    update_data = ProjectUpdate(title="Updated")
    with pytest.raises(HTTPException) as exc_info:
        project_service.update_project(db_session, project_id=999, project_in=update_data)
    assert exc_info.value.status_code == 404
    assert "Project not found" in exc_info.value.detail