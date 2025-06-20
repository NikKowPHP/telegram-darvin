import pytest
from decimal import Decimal
from sqlalchemy.orm import Session
from app.services.credit_transaction_service import CreditTransactionService
from app.models.user import User
from app.models.api_key_usage import APIKeyUsage
from app.schemas.credit_transaction import CreditTransactionCreate

@pytest.fixture
def credit_service(db_session: Session):
    return CreditTransactionService()

def test_record_transaction_sufficient_credits(credit_service, db_session: Session):
    user = User(credit_balance=Decimal('100.00'))
    db_session.add(user)
    db_session.commit()
    
    transaction_data = CreditTransactionCreate(
        user_id=user.id,
        credits_amount=Decimal('-50.00'),
        description="Test deduction"
    )
    
    result = credit_service.record_transaction(db_session, transaction_data)
    assert result.credits_amount == Decimal('-50.00')
    assert db_session.query(User).get(user.id).credit_balance == Decimal('50.00')

def test_record_transaction_insufficient_credits(credit_service, db_session: Session):
    user = User(credit_balance=Decimal('10.00'))
    db_session.add(user)
    db_session.commit()
    
    transaction_data = CreditTransactionCreate(
        user_id=user.id,
        credits_amount=Decimal('-50.00'),
        description="Test deduction"
    )
    
    with pytest.raises(ValueError) as exc_info:
        credit_service.record_transaction(db_session, transaction_data)
    assert "Insufficient credits" in str(exc_info.value)
    assert db_session.query(User).get(user.id).credit_balance == Decimal('10.00')

def test_record_transaction_with_api_usage(credit_service, db_session: Session):
    user = User(credit_balance=Decimal('100.00'))
    api_usage = APIKeyUsage(
        user_id=user.id,
        input_tokens=1000,
        output_tokens=2000
    )
    db_session.add_all([user, api_usage])
    db_session.commit()
    
    transaction_data = CreditTransactionCreate(
        user_id=user.id,
        api_key_usage_id=api_usage.id,
        credits_amount=Decimal('-5.00'),
        description="API usage"
    )
    
    result = credit_service.record_transaction(db_session, transaction_data)
    assert result.api_key_usage_id == api_usage.id
    assert result.real_cost_associated_usd > Decimal('0')

def test_exact_credit_match(credit_service, db_session: Session):
    """Test transaction when user has exactly enough credits"""
    user = User(credit_balance=Decimal('50.00'))
    db_session.add(user)
    db_session.commit()
    
    transaction_data = CreditTransactionCreate(
        user_id=user.id,
        credits_amount=Decimal('-50.00'),
        description="Exact amount test"
    )
    
    result = credit_service.record_transaction(db_session, transaction_data)
    assert result.credits_amount == Decimal('-50.00')
    assert db_session.query(User).get(user.id).credit_balance == Decimal('0.00')

@pytest.mark.asyncio
async def test_concurrent_transactions(credit_service, db_session: Session):
    """Test concurrent transactions don't cause race conditions"""
    user = User(credit_balance=Decimal('100.00'))
    db_session.add(user)
    db_session.commit()
    
    async def make_transaction(amount):
        with db_session.begin():
            transaction_data = CreditTransactionCreate(
                user_id=user.id,
                credits_amount=Decimal(amount),
                description="Concurrent test"
            )
            return credit_service.record_transaction(db_session, transaction_data)
    
    # Run multiple transactions concurrently
    results = await asyncio.gather(
        make_transaction('-30.00'),
        make_transaction('-20.00'),
        make_transaction('-15.00')
    )
    
    final_balance = db_session.query(User).get(user.id).credit_balance
    assert final_balance == Decimal('35.00')  # 100 - 30 - 20 - 15 = 35

def test_transaction_rollback(credit_service, db_session: Session):
    """Test that failed transactions roll back credit deductions"""
    user = User(credit_balance=Decimal('100.00'))
    db_session.add(user)
    db_session.commit()
    
    class TestException(Exception):
        pass
    
    try:
        with db_session.begin():
            transaction_data = CreditTransactionCreate(
                user_id=user.id,
                credits_amount=Decimal('-50.00'),
                description="Rollback test"
            )
            credit_service.record_transaction(db_session, transaction_data)
            raise TestException("Simulated error")
    except TestException:
        pass
    
    assert db_session.query(User).get(user.id).credit_balance == Decimal('100.00')

def test_invalid_transaction_amounts(credit_service, db_session: Session):
    """Test various invalid transaction amounts"""
    user = User(credit_balance=Decimal('100.00'))
    db_session.add(user)
    db_session.commit()
    
    # Test zero amount
    with pytest.raises(ValueError):
        transaction_data = CreditTransactionCreate(
            user_id=user.id,
            credits_amount=Decimal('0.00'),
            description="Invalid amount"
        )
        credit_service.record_transaction(db_session, transaction_data)
    
    # Test positive deduction
    with pytest.raises(ValueError):
        transaction_data = CreditTransactionCreate(
            user_id=user.id,
            credits_amount=Decimal('50.00'),
            description="Invalid amount"
        )
        credit_service.record_transaction(db_session, transaction_data)