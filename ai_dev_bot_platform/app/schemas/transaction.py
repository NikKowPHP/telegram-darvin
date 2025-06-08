from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import datetime
import uuid

class CreditTransactionBase(BaseModel):
    user_id: int
    project_id: Optional[uuid.UUID] = None
    api_key_usage_id: Optional[int] = None
    transaction_type: str  # 'initial_grant', 'purchase', 'usage_deduction'
    credits_amount: Decimal
    real_cost_associated_usd: Optional[Decimal] = None
    external_transaction_id: Optional[str] = None
    description: Optional[str] = None

class CreditTransactionCreate(CreditTransactionBase):
    pass

class CreditTransactionUpdate(BaseModel):
    credits_amount: Optional[Decimal] = None
    real_cost_associated_usd: Optional[Decimal] = None
    description: Optional[str] = None

class CreditTransactionInDB(CreditTransactionBase):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True