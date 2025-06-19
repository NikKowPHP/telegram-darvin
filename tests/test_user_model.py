import pytest
from datetime import datetime
from app.models.user import User
from app.schemas.user import UserCreate

def test_user_creation():
    """Test user creation with automatic timestamps"""
    user_data = {
        "telegram_user_id": 12345,
        "username": "testuser",
        "email": "test@example.com"
    }
    
    # Should create successfully without explicit timestamps
    user = User(**user_data)
    
    assert user.telegram_user_id == 12345
    assert isinstance(user.created_at, datetime)
    assert isinstance(user.updated_at, datetime)

def test_user_schema_validation():
    """Test user schema validation"""
    user_data = {
        "telegram_user_id": 12345,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "credit_balance": 100.00
    }
    
    # Should validate successfully with proper datetime values
    user = UserCreate(**user_data)
    
    assert user.telegram_user_id == 12345