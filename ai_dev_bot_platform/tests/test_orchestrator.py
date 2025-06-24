import pytest
import uuid
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime
from app.services.orchestrator_service import ModelOrchestrator
from app.schemas.user import User


@pytest.mark.asyncio
async def test_handle_new_project_flow(mocker):
    # 1. Setup
    mock_db = MagicMock()

    # Mock the services that the orchestrator initializes
    mocker.patch("app.services.orchestrator_service.APIKeyManager")
    mocker.patch("app.services.orchestrator_service.LLMClient")
    mock_architect_agent = mocker.patch(
        "app.services.orchestrator_service.ArchitectAgent"
    )
    mocker.patch("app.services.orchestrator_service.ImplementerAgent")
    mock_project_service = mocker.patch(
        "app.services.orchestrator_service.ProjectService"
    )
    mock_storage_service = mocker.patch(
        "app.services.orchestrator_service.StorageService"
    )
    # ... mock other services if needed

    # Instantiate the orchestrator (its __init__ will use the mocked classes)
    orchestrator = ModelOrchestrator(mock_db)

    # Configure the mocks to return expected values
    fake_project_id = uuid.uuid4()
    mock_project_service.return_value.create_project.return_value = MagicMock(
        id=fake_project_id, title="Fake Project"
    )
    mock_architect_agent.return_value.generate_initial_plan_and_docs = AsyncMock(
        return_value={
            "todo_list_markdown": "[ ] Task 1",
            "tech_stack_suggestion": {},
            "llm_call_details": {
                "model_name_used": "fake-model"
            },  # For credit deduction
        }
    )

    # Mock the credit deduction method so it doesn't run real logic
    orchestrator._deduct_credits_for_llm_call = AsyncMock()

    # 2. Action
    test_user = User(
        id=1,
        telegram_user_id=123,
        credit_balance=100,
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1)
    )
    result = await orchestrator._handle_new_project(test_user, "create a new web app")

    # 3. Assert
    mock_project_service.return_value.create_project.assert_called_once()
    mock_architect_agent.return_value.generate_initial_plan_and_docs.assert_awaited_once()
    orchestrator._deduct_credits_for_llm_call.assert_awaited_once()
    mock_project_service.return_value.update_project.assert_called_once()
    mock_storage_service.return_value.create_bucket.assert_called_once()
    assert "Project 'Fake Project' created!" in result["text"]


@pytest.mark.asyncio
async def test_handle_refine_request_flow(mocker):
    # 1. Setup
    mock_db = MagicMock()

    # Mock services
    mocker.patch("app.services.orchestrator_service.APIKeyManager")
    mocker.patch("app.services.orchestrator_service.LLMClient")
    mocker.patch("app.services.orchestrator_service.ArchitectAgent")
    mock_implementer_agent = mocker.patch(
        "app.services.orchestrator_service.ImplementerAgent"
    )
    mock_project_service = mocker.patch(
        "app.services.orchestrator_service.ProjectService"
    )
    mock_file_service = mocker.patch(
        "app.services.orchestrator_service.ProjectFileService"
    )
    mock_storage_service = mocker.patch(
        "app.services.orchestrator_service.StorageService"
    )

    # Instantiate the orchestrator
    orchestrator = ModelOrchestrator(mock_db)

    # Configure mocks
    fake_project_id = uuid.uuid4()
    mock_project_service.return_value.get_project.return_value = MagicMock(
        id=fake_project_id
    )
    mock_storage_service.return_value.download_file.return_value = "original code"
    mock_implementer_agent.return_value.apply_changes_with_aider = AsyncMock(
        return_value={"status": "success"}
    )

    # 2. Action
    test_user = User(
        id=1,
        telegram_user_id=123,
        credit_balance=100,
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1)
    )
    await orchestrator._handle_refine_request(
        test_user, str(fake_project_id), "src/main.py", "add a comment"
    )

    # 3. Assert
    mock_storage_service.return_value.download_file.assert_called_once_with(
        str(fake_project_id), "src/main.py"
    )
    mock_implementer_agent.return_value.apply_changes_with_aider.assert_awaited_once()
    mock_storage_service.return_value.upload_file.assert_called_once()
    mock_file_service.return_value.update_file_content.assert_called_once()
