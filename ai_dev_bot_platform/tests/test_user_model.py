import pytest
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.db.session import SessionLocal


def test_user_model_timestamp_fields():
    """Test that User model correctly handles timestamp fields."""
    db = SessionLocal()

    try:
        # Test creating a user with valid timestamps
        user = User(
            telegram_user_id=12345,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            credit_balance=10.0,
        )
        db.add(user)
        db.commit()

        # Refresh to get the ID
        db.refresh(user)
        assert user.id is not None
        assert user.created_at is not None
        assert user.updated_at is not None

        # Test that timestamps are properly updated on update
        user.credit_balance = 15.0
        user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)
        assert user.updated_at > user.created_at

        # Test that created_at is not changed on update
        original_created_at = user.created_at
        user.credit_balance = 20.0
        user.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)
        assert user.created_at == original_created_at

    finally:
        # Clean up
        db.query(User).filter(User.telegram_user_id == 12345).delete()
        db.commit()
        db.close()


def test_user_model_timestamp_validation():
    """Test that User model rejects invalid timestamp values."""
    db = SessionLocal()

    try:
        # Test that None values for timestamps are rejected
        with pytest.raises(IntegrityError):
            user = User(
                telegram_user_id=67890,
                created_at=None,
                updated_at=None,
                credit_balance=10.0,
            )
            db.add(user)
            db.commit()

    finally:
        # Clean up any partially added records
        db.rollback()
        db.close()
