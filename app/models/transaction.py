# ROO-AUDIT-TAG :: feature-008-credit-monetization.md :: Implement credit transaction logging
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.session import Base

class Transaction(Base):
    """Model for tracking credit transactions."""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum("purchase", "usage", name="transaction_types"), nullable=False)
    amount = Column(Float)
    credits = Column(Integer, nullable=False)
    status = Column(Enum("completed", "failed", name="transaction_statuses"), default="completed")
    created_at = Column(DateTime, default=datetime.utcnow)
    description = Column(String)

    user = relationship("User", back_populates="transactions")

# ROO-AUDIT-TAG :: feature-008-credit-monetization.md :: END