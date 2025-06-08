from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from typing import Optional, List
from decimal import Decimal

def get_user_by_telegram_id(db: Session, telegram_user_id: int) -> Optional[User]:
    return db.query(User).filter(User.telegram_user_id == telegram_user_id).first()

def create_user(db: Session, user_in: UserCreate, initial_credits: Decimal = Decimal("10.00")) -> User: # Example initial credits
    db_user = User(
        telegram_user_id=user_in.telegram_user_id,
        username=user_in.username,
        email=user_in.email,
        credit_balance=initial_credits # Grant initial credits
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_credits(db: Session, telegram_user_id: int, amount: Decimal, is_deduction: bool = True) -> Optional[User]:
    db_user = get_user_by_telegram_id(db, telegram_user_id)
    if db_user:
        if is_deduction:
            if db_user.credit_balance < amount:
                # Handle insufficient credits (raise error or return None/False)
                # For now, let's just not deduct if insufficient
                return None # Or raise an exception
            db_user.credit_balance -= amount
        else:
            db_user.credit_balance += amount
        db.commit()
        db.refresh(db_user)
    return db_user
# Add other update/get methods as needed