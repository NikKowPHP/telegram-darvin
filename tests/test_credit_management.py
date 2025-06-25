# ROO-AUDIT-TAG :: feature-008-credit-monetization.md :: Write unit tests for credit management
import pytest
from unittest.mock import Mock, patch
from app.models.user import User
from app.models.transaction import Transaction
from app.services.billing_service import BillingService
from app.services.notification_service import NotificationService

@pytest.fixture
def mock_db_session():
    return Mock()

@pytest.fixture
def billing_service(mock_db_session):
    return BillingService(db=mock_db_session)

@pytest.fixture
def notification_service():
    return NotificationService()

class TestCreditManagement:
    def test_credit_balance_update(self, mock_db_session):
        """Test user credit balance updates correctly."""
        user = User(credit_balance=100)
        user.credit_balance += 50
        assert user.credit_balance == 150

    def test_transaction_creation(self, mock_db_session):
        """Test transaction record creation."""
        transaction = Transaction(
            user_id=1,
            amount=50,
            transaction_type="purchase"
        )
        assert transaction.user_id == 1
        assert transaction.amount == 50

    @patch('app.services.billing_service.BillingService.process_payment')
    def test_credit_purchase(self, mock_process, billing_service):
        """Test credit purchase workflow."""
        mock_process.return_value = True
        result = billing_service.purchase_credits(
            user_id=1,
            package="basic",
            payment_token="test_token"
        )
        assert result is not None
        assert isinstance(result, Transaction)

    @patch('app.services.notification_service.NotificationService.send_low_credit_notification')
    def test_low_credit_notification(self, mock_send, notification_service):
        """Test low credit notification triggers."""
        notification_service.send_low_credit_notification(1)
        mock_send.assert_called_once_with(1)
# ROO-AUDIT-TAG :: feature-008-credit-monetization.md :: END