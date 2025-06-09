import pytest
from unittest.mock import MagicMock
from app.services.user_service import UserService
from app.models.user import User
from decimal import Decimal

def test_get_user_by_telegram_id():
    # 1. Setup
    mock_db_session = MagicMock()
    user_service = UserService()
    
    test_user_id = 12345
    expected_user = User(
        id=1, 
        telegram_user_id=test_user_id, 
        username="testuser", 
        credit_balance=Decimal("10.00")
    )

    # 2. Mock the DB call
    mock_db_session.query.return_value.filter.return_value.first.return_value = expected_user
    
    # 3. Action
    result_user = user_service.get_user_by_telegram_id(mock_db_session, telegram_user_id=test_user_id)
    
    # 4. Assert
    assert result_user is not None
    assert result_user.telegram_user_id == test_user_id
    assert result_user.username == "testuser"
    mock_db_session.query.return_value.filter.return_value.first.assert_called_once()