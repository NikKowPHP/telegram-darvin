from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.billing_service import CreditTransactionService
from app.schemas.transaction import CreditTransactionCreate
from typing import Optional, List
from decimal import Decimal


class UserService:
    def get_user_by_telegram_id(
        self, db: Session, telegram_user_id: int
    ) -> Optional[User]:
        return db.query(User).filter(User.telegram_user_id == telegram_user_id).first()

    def create_user(
        self,
        db: Session,
        user_in: UserCreate,
        initial_credits: Decimal = Decimal("10.00"),
    ) -> User:
        db_user = User(
            telegram_user_id=user_in.telegram_user_id,
            username=user_in.username,
            email=user_in.email,
            credit_balance=initial_credits,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def update_user_credits(
        self,
        db: Session,
        telegram_user_id: int,
        amount: Decimal,
        is_deduction: bool = True,
    ) -> Optional[User]:
        db_user = self.get_user_by_telegram_id(db, telegram_user_id)
        if db_user:
            if is_deduction:
                if db_user.credit_balance < amount:
                    return None  # Insufficient credits
                db_user.credit_balance -= amount
            else:
                db_user.credit_balance += amount
            db.commit()
            db.refresh(db_user)
        return db_user

    def add_credits_after_purchase(
        self, db: Session, user_id: int, credit_package: str
    ) -> Optional[User]:
        """Simulates a successful credit purchase."""
        credit_amounts = {
            "buy_100": Decimal("100.00"),
            "buy_500": Decimal("500.00"),
        }
        amount_to_add = credit_amounts.get(credit_package)
        if not amount_to_add:
            return None

        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None

        db_user.credit_balance += amount_to_add

        # Record the transaction
        transaction_service = CreditTransactionService()
        transaction_in = CreditTransactionCreate(
            user_id=user_id,
            transaction_type="purchase",
            credits_amount=amount_to_add,
            description=f"Simulated purchase of {credit_package}",
        )
        transaction_service.record_transaction(db, transaction_in)

        db.commit()
        db.refresh(db_user)
        return db_user
