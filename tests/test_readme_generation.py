# ROO-AUDIT-TAG :: feature-007-readme-generation.md :: Write integration tests for README generation
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.agents.architect_agent import ArchitectAgent
from app.schemas.project import Project
from app.utils.llm_client import LLMClient
from main import app

@pytest.fixture
def mock_llm_client():
    client = AsyncMock(spec=LLMClient)
    client.call_llm.return_value = {
        "text_response": """# Test Project

## Overview
Test Project Overview

## Features
- Feature 1
- Feature 2

## Setup
```bash
pip install -r requirements.txt
```

## Configuration
Set these environment variables:
- API_KEY
- DB_URL

## Usage
```python
from app import main
main.run()
```

## Deployment
Deploy to cloud using Docker""",
        "input_tokens": 100,
        "output_tokens": 200
    }
    return client

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def sample_project():
    return Project(
        id="test-project",
        title="Test Project",
        description="Test Description",
        tech_stack={
            "dependencies": ["python3.8", "fastapi"],
            "environment_variables": {"API_KEY": "secret"}
        }
    )

@pytest.mark.asyncio
async def test_readme_generation_basic_structure(mock_llm_client, sample_project):
    architect = ArchitectAgent(mock_llm_client)
    readme = await architect.generate_readme(sample_project.dict())
    
    required_sections = [
        "# Test Project",
        "## Overview",
        "## Features",
        "## Setup",
        "## Configuration",
        "## Usage",
        "## Deployment"
    ]
    
    for section in required_sections:
        assert section in readme, f"Missing section: {section}"

@pytest.mark.asyncio
async def test_readme_includes_tech_stack_details(mock_llm_client, sample_project):
    architect = ArchitectAgent(mock_llm_client)
    readme = await architect.generate_readme(sample_project.dict())
    
    required_tech = [
        "python3.8",
        "fastapi",
        "API_KEY",
        "DB_URL",
        "pip install",
        "Docker"
    ]
    
    for tech in required_tech:
        assert tech in readme, f"Missing tech reference: {tech}"

@pytest.mark.asyncio
async def test_readme_error_handling(mock_llm_client, sample_project):
    mock_llm_client.call_llm.return_value = {
        "text_response": "ERROR: Invalid project format",
        "input_tokens": 100,
        "output_tokens": 200
    }
    architect = ArchitectAgent(mock_llm_client)
    readme = await architect.generate_readme(sample_project.dict())
    
    assert "ERROR" in readme
    assert "Invalid project format" in readme

def test_readme_generation_api(test_client, mock_llm_client, sample_project):
    with patch('app.api.endpoints.orchestrator.LLMClient', return_value=mock_llm_client):
        response = test_client.post(
            "/api/generate-readme",
            json=sample_project.dict()
        )
        
        assert response.status_code == 200
        assert "readme" in response.json()
        assert response.json()["status"] == "success"
        
        readme = response.json()["readme"]
        assert "# Test Project" in readme
        assert "## Setup" in readme

def test_readme_generation_api_error_handling(test_client, mock_llm_client, sample_project):
    mock_llm_client.call_llm.return_value = {
        "text_response": "ERROR: Invalid input",
        "input_tokens": 100,
        "output_tokens": 200
    }
    
    with patch('app.api.endpoints.orchestrator.LLMClient', return_value=mock_llm_client):
        response = test_client.post(
            "/api/generate-readme",
            json={"invalid": "data"}
        )
        
        assert response.status_code == 500
        assert "error" in response.json()
        assert "README generation failed" in response.json()["detail"]
# ROO-AUDIT-TAG :: feature-007-readme-generation.md :: END