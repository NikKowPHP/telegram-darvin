import pytest
from unittest.mock import AsyncMock
from ai_dev_bot_platform.app.telegram_bot.requirement_gathering import handle_requirement_message
from ai_dev_bot_platform.app.agents.architect_agent import ArchitectAgent
from ai_dev_bot_platform.app.agents.implementer_agent import ImplementerAgent
from app.schemas.project import Project
from app.core.config import settings

@pytest.mark.asyncio
async def test_requirement_gathering_extraction():
    """Test requirement extraction from user messages"""
    update = AsyncMock()
    update.message.text = "I need a login system using JWT tokens"
    context = AsyncMock()
    context.user_data = {'conversation_id': 'test123'}
    
    await handle_requirement_message(update, context)
    
    # Verify response contains extracted features and technologies
    update.message.reply_text.assert_called()
    response = update.message.reply_text.call_args[0][0]
    assert "login system" in response
    assert "JWT tokens" in response

@pytest.mark.asyncio
async def test_architect_verification():
    """Test architect agent verification logic"""
    llm_client = AsyncMock()
    architect = ArchitectAgent(llm_client)
    project = Project(
        id="test",
        title="Test Project",
        description="Test Description"
    )
    
    # Mock LLM response with structured verification report
    llm_client.call_llm.return_value = {
        "text_response": "VERIFICATION REPORT:\nfunctional correctness: Passed\ncode quality: Good\nsecurity: No issues found"
    }
    
    result = await architect.verify_implementation_step(
        project=project,
        code_snippet="def test(): pass",
        relevant_docs="Test docs",
        todo_item="Test implementation"
    )
    
    assert "functional correctness" in result["verification_criteria"]
    assert result["status"] in ["APPROVED", "NEEDS_REVISION"]

@pytest.mark.asyncio
async def test_implementer_tdd_cycle():
    """Test implementer agent TDD workflow"""
    llm_client = AsyncMock()
    implementer = ImplementerAgent(llm_client)
    
    # Mock LLM responses for test generation and implementation
    llm_client.call_llm.side_effect = [
        {"text_response": "def test_feature(): assert True"},
        {"text_response": "def feature(): return True"}
    ]
    
    result = await implementer.run_tdd_cycle(
        project_root="/test",
        task_description="Implement test feature"
    )
    
    assert "test_code" in result
    assert "code" in result
    assert result.get("success", False)

if __name__ == "__main__":
    pytest.main(["-v", __file__])