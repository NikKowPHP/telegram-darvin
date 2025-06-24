import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.services.orchestrator_service import ModelOrchestrator
from app.schemas.user import User
from app.telegram_bot.requirement_gathering import RequirementState


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def orchestrator(mock_db):
    return ModelOrchestrator(mock_db)


@pytest.fixture
def mock_user():
    user = MagicMock(spec=User)
    user.id = 1
    user.telegram_user_id = 12345
    user.credit_balance = 10.0
    return user


@pytest.mark.asyncio
async def test_planning_task_routing(orchestrator, mock_user, mock_db):
    """Test that planning tasks are routed to the architect agent"""
    with patch.object(
        orchestrator.architect_agent,
        "generate_plan",
        return_value={
            "plan_filename": "plan.md",
            "plan_content": "Sample plan content",
            "llm_call_details": {
                "model_name_used": "test-model",
                "input_tokens": 100,
                "output_tokens": 150,
            },
        },
    ) as mock_generate_plan:

        # Mock project and project service
        mock_project = MagicMock()
        mock_project.id = "test-project-id"
        mock_project.current_todo_markdown = "- [ ] Plan the architecture"
        mock_project.description = "Test project"
        mock_project.tech_stack = {}
        mock_project.user_id = 1

        mock_db.get.return_value = mock_project

        # Call the method
        result = await orchestrator._handle_plan_task(
            user=mock_user, project_id="test-project-id", task_index=1
        )

        # Assertions
        assert mock_generate_plan.called
        assert result["text"].startswith(
            "Planning task 'Plan the architecture' completed!"
        )
        assert "Plan file: plan.md" in result["text"]


@pytest.mark.asyncio
async def test_implementation_task_routing(orchestrator, mock_user, mock_db):
    """Test that implementation tasks are routed to the implementer agent"""
    with patch.object(
        orchestrator.implementer_agent,
        "implement_todo_item",
        return_value={
            "filename": "app.py",
            "code": "print('Hello, world!')",
            "llm_call_details": {
                "model_name_used": "test-model",
                "input_tokens": 100,
                "output_tokens": 150,
            },
        },
    ) as mock_implement:

        # Mock project and project service
        mock_project = MagicMock()
        mock_project.id = "test-project-id"
        mock_project.current_todo_markdown = "- [ ] Implement the app"
        mock_project.description = "Test project"
        mock_project.tech_stack = {}
        mock_project.user_id = 1

        mock_db.get.return_value = mock_project

        # Call the method
        result = await orchestrator._handle_implement_task(
            user=mock_user, project_id="test-project-id", task_index=1
        )

        # Assertions
        assert mock_implement.called
        assert "Task 'Implement the app' implemented" in result["text"]


@pytest.mark.asyncio
async def test_message_handler_routing(orchestrator, mock_user, mock_db):
    """Test that the message handler correctly routes different task types"""
    with patch(
        "app.telegram_bot.handlers.is_in_requirement_gathering", return_value=False
    ), patch("app.telegram_bot.handlers.get_orchestrator", return_value=orchestrator):

        # Mock update and context
        mock_update = MagicMock()
        mock_update.effective_user.id = 12345
        mock_update.message.text = "plan task 1 of project test-project-id"
        mock_update.effective_chat.id = 12345

        mock_context = MagicMock()
        mock_context.user_data = {}

        # Call the message handler
        from app.telegram_bot.handlers import message_handler

        await message_handler(mock_update, mock_context)

        # Check that the architect agent was called
        assert orchestrator.architect_agent.generate_plan.called

        # Reset mocks
        orchestrator.architect_agent.generate_plan.reset_mock()
        mock_update.message.text = "implement task 1 of project test-project-id"

        # Call the message handler again
        await message_handler(mock_update, mock_context)

        # Check that the implementer agent was called
        assert orchestrator.implementer_agent.implement_todo_item.called
