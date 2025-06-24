from sqlalchemy import Column, Integer, String, BigInteger, DateTime, DECIMAL
from sqlalchemy.sql import func
from app.db.session import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    telegram_user_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    credit_balance = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
