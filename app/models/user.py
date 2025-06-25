# ROO-AUDIT-TAG :: feature-008-credit-monetization.md :: Add credit balance field to User model
from sqlalchemy import Column, Integer, String
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    # ROO-AUDIT-TAG :: feature-008-credit-monetization.md :: Implement credit balance field
    credit_balance = Column(Integer, default=0)

# ROO-AUDIT-TAG :: feature-008-credit-monetization.md :: END