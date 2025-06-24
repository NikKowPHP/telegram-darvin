import pytest
from unittest.mock import AsyncMock
from app.agents.architect_agent import ArchitectAgent
from app.schemas.project import Project
from app.utils.llm_client import LLMClient

@pytest.fixture
def mock_llm_client():
    client = AsyncMock(spec=LLMClient)
    client.call_llm.return_value = {
        "text_response": """## Overview
Test Project Overview

## Setup
Install with pip

## Configuration
Set environment variables

## Usage
Run main.py

## Deployment
Deploy to cloud""",
        "input_tokens": 100,
        "output_tokens": 200
    }
    return client

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
    readme = await architect.generate_readme(sample_project)
    
    assert "## Overview" in readme
    assert "## Setup" in readme
    assert "## Configuration" in readme
    assert "## Usage" in readme
    assert "## Deployment" in readme
    assert "Test Project" in readme

@pytest.mark.asyncio
async def test_readme_includes_tech_stack_details(mock_llm_client, sample_project):
    architect = ArchitectAgent(mock_llm_client)
    readme = await architect.generate_readme(sample_project)
    
    assert "python3.8" in readme
    assert "fastapi" in readme
    assert "API_KEY" in readme

@pytest.mark.asyncio
async def test_readme_error_handling(mock_llm_client, sample_project):
    mock_llm_client.call_llm.return_value = {
        "text_response": "Error: Invalid project",
        "input_tokens": 100,
        "output_tokens": 200
    }
    architect = ArchitectAgent(mock_llm_client)
    readme = await architect.generate_readme(sample_project)
    
    assert "ERROR" in readme