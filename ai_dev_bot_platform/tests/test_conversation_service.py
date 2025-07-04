# ROO-AUDIT-TAG :: feature-001-requirement-gathering.md :: Write unit tests for conversation service
import pytest
from unittest.mock import Mock, call
from datetime import datetime
from app.services.conversation_service import ConversationService
from app.models.conversation_model import Conversation
from app.schemas.conversation import MessageBase
from pydantic import ValidationError

@pytest.fixture
def mock_db():
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = Conversation(
        id="conv123",
        user_id="user123",
        messages=[]
    )
    return db

def test_start_conversation(mock_db):
    service = ConversationService(mock_db)
    conversation = service.start_conversation("user123", "project456")
    
    assert conversation.user_id == "user123"
    assert conversation.project_id == "project456"
    assert isinstance(conversation.id, str)
    assert len(conversation.messages) == 0
    
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(conversation)

def test_add_message_valid(mock_db):
    service = ConversationService(mock_db)
    test_message = {
        "content": "Hello world",
        "role": "user",
        "timestamp": datetime.now().isoformat()
    }
    
    conversation = service.add_message("conv123", test_message)
    assert len(conversation.messages) == 1
    assert conversation.messages[0]["content"] == "Hello world"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(conversation)

def test_add_message_invalid(mock_db):
    service = ConversationService(mock_db)
    invalid_message = {"content": "", "role": "invalid"}
    
    with pytest.raises(ValidationError):
        service.add_message("conv123", invalid_message)

def test_get_conversation_exists(mock_db):
    service = ConversationService(mock_db)
    conversation = service.get_conversation("conv123")
    assert conversation.id == "conv123"
    mock_db.query.assert_called_once_with(Conversation)

def test_get_conversation_not_exists(mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    service = ConversationService(mock_db)
    result = service.get_conversation("bad-id")
    assert result is None
# ROO-AUDIT-TAG :: feature-001-requirement-gathering.md :: END