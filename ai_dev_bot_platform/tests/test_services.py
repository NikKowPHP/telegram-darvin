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
        credit_balance=Decimal("10.00"),
    )

    # 2. Mock the DB call
    mock_db_session.query.return_value.filter.return_value.first.return_value = (
        expected_user
    )

    # 3. Action
    result_user = user_service.get_user_by_telegram_id(
        mock_db_session, telegram_user_id=test_user_id
    )

    # 4. Assert
    assert result_user is not None
    assert result_user.telegram_user_id == test_user_id
    assert result_user.username == "testuser"
    mock_db_session.query.return_value.filter.return_value.first.assert_called_once()


from app.services.project_service import ProjectService
from app.schemas.project import ProjectCreate


def test_create_project():
    # 1. Setup
    mock_db_session = MagicMock()
    project_service = ProjectService()

    user_id = 1
    project_in = ProjectCreate(
        user_id=user_id, title="Test Project", description="A test description."
    )

    # 2. Action
    project_service.create_project(mock_db_session, project_in, user_id=user_id)

    # 3. Assert
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

    # Check the object passed to add()
    added_object = mock_db_session.add.call_args[0][0]
    assert added_object.title == "Test Project"
    assert added_object.user_id == user_id


from app.services.billing_service import CreditTransactionService
from app.schemas.transaction import CreditTransactionCreate


def test_record_transaction():
    # 1. Setup
    mock_db_session = MagicMock()
    transaction_service = CreditTransactionService()

    transaction_in = CreditTransactionCreate(
        user_id=1, transaction_type="purchase", credits_amount=Decimal("100.00")
    )

    # 2. Action
    transaction_service.record_transaction(mock_db_session, transaction_in)

    # 3. Assert
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()
    added_object = mock_db_session.add.call_args[0][0]
    assert added_object.credits_amount == Decimal("100.00")


from app.services.payment_service import PaymentService


def test_create_checkout_session(mocker):
    # 1. Setup
    mock_stripe_session = mocker.patch("stripe.checkout.Session.create")
    mock_stripe_session.return_value = {"url": "https://fake.stripe.url/session123"}

    payment_service = PaymentService()
    # This user object is simplified for testing purposes
    mock_user = User(id=1, telegram_user_id=12345)

    # 2. Action
    result_url = payment_service.create_checkout_session(
        user=mock_user, credit_package="buy_100"
    )

    # 3. Assert
    assert result_url == "https://fake.stripe.url/session123"
    mock_stripe_session.assert_called_once()
    # Verify that our internal user ID was passed to Stripe
    assert mock_stripe_session.call_args[1]["client_reference_id"] == "1"
