from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey, TEXT
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.session import Base


class CreditTransaction(Base):
    __tablename__ = "credit_transactions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    api_key_usage_id = Column(Integer, ForeignKey("api_key_usage.id"), nullable=True)
    transaction_type = Column(
        String(50), nullable=False
    )  # 'initial_grant', 'purchase', 'usage_deduction'
    credits_amount = Column(
        DECIMAL(10, 2), nullable=False
    )  # Positive for add, negative for deduct
    real_cost_associated_usd = Column(DECIMAL(10, 6), nullable=True)
    external_transaction_id = Column(String(255), nullable=True)  # For Stripe, etc.
    description = Column(TEXT, nullable=True)
    created_at = Column(DateTime, default=func.now())
