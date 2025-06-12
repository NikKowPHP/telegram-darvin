# Phase 4 Implementation Todo - Monetization & User Management

**Project Goal:** Implement database models and services for tracking costs and credits, integrate credit deduction into the orchestrator, and add basic user-facing credit commands.

## Task 1: Define `model_pricing` SQLAlchemy Model & Pydantic Schema
- **File:** `ai_dev_bot_platform/app/models/api_key_models.py`
- **Action:** Add the following `ModelPricing` class:
```python
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Boolean, TEXT
from sqlalchemy.sql import func
from app.db.session import Base

class ModelPricing(Base):
    __tablename__ = "model_pricing"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model_provider = Column(String(100), nullable=False) # 'google', 'openrouter'
    model_name = Column(String(255), nullable=False, unique=True) # 'gemini-1.5-pro-latest', 'openrouter/anthropic/claude-3-opus'
    input_cost_per_million_tokens = Column(DECIMAL(12, 6), nullable=False)
    output_cost_per_million_tokens = Column(DECIMAL(12, 6), nullable=False)
    image_input_cost_per_image = Column(DECIMAL(12, 6), nullable=True)
    image_output_cost_per_image = Column(DECIMAL(12, 6), nullable=True)
    currency = Column(String(10), nullable=False, default='USD')
    notes = Column(TEXT, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
```
- **File:** `ai_dev_bot_platform/app/schemas/api_key_schemas.py`
- **Action:** Add the following `ModelPricing` schemas:
```python
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import datetime

class ModelPricingBase(BaseModel):
    model_provider: str
    model_name: str
    input_cost_per_million_tokens: Decimal
    output_cost_per_million_tokens: Decimal
    image_input_cost_per_image: Optional[Decimal] = None
    image_output_cost_per_image: Optional[Decimal] = None
    currency: str = 'USD'
    notes: Optional[str] = None
    is_active: bool = True

class ModelPricingCreate(ModelPricingBase):
    pass

class ModelPricingUpdate(BaseModel): # Allow partial updates
    input_cost_per_million_tokens: Optional[Decimal] = None
    output_cost_per_million_tokens: Optional[Decimal] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None

class ModelPricingInDB(ModelPricingBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    class Config:
        from_attributes = True
```
- **Verification:** Model and schema files created. Table `model_pricing` exists in DB.

## Task 2: Define `api_key_usage` SQLAlchemy Model & Pydantic Schema
- **File:** `ai_dev_bot_platform/app/models/api_key_models.py`
- **Action:** Add the following `APIKeyUsage` class:
```python
import uuid
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from typing import Optional

class APIKeyUsage(Base):
    __tablename__ = "api_key_usage"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True) # Changed to Integer Serial for simplicity
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    api_key_identifier: Optional[str] = Column(String(100), nullable=True) # e.g. part of the key or a friendly name
    model_provider = Column(String(100), nullable=False) # 'google', 'openrouter'
    model_name = Column(String(255), nullable=False)
    task_type = Column(String(100), nullable=True) # 'planning', 'coding', 'verification'
    input_tokens_used = Column(Integer, default=0)
    output_tokens_used = Column(Integer, default=0)
    images_processed = Column(Integer, default=0)
    actual_cost_usd = Column(DECIMAL(10, 6), nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())
```
- **File:** `ai_dev_bot_platform/app/schemas/api_key_schemas.py`
- **Action:** Add the following `APIKeyUsage` schemas:
```python
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import datetime
import uuid

class APIKeyUsageBase(BaseModel):
    project_id: Optional[uuid.UUID] = None
    user_id: Optional[int] = None
    api_key_identifier: Optional[str] = None
    model_provider: str
    model_name: str
    task_type: Optional[str] = None
    input_tokens_used: int = 0
    output_tokens_used: int = 0
    images_processed: int = 0
    actual_cost_usd: Optional[Decimal] = None
    response_time_ms: Optional[int] = None

class APIKeyUsageCreate(APIKeyUsageBase):
    pass # All fields provided at creation

class APIKeyUsageInDB(APIKeyUsageBase):
    id: int
    created_at: datetime.datetime
    class Config:
        from_attributes = True
```
- **Verification:** Model and schema files created. Table `api_key_usage` exists.

## Task 3: Define `credit_transactions` SQLAlchemy Model & Pydantic Schema
- **File:** `ai_dev_bot_platform/app/models/transaction.py`
- **Action:** Add the following `CreditTransaction` class:
```python
import uuid
from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, ForeignKey, TEXT
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.session import Base

class CreditTransaction(Base):
    __tablename__ = "credit_transactions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True) # Simpler PK
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    api_key_usage_id = Column(Integer, ForeignKey("api_key_usage.id"), nullable=True)
    transaction_type = Column(String(50), nullable=False) # 'initial_grant', 'purchase', 'usage_deduction', etc.
    credits_amount = Column(DECIMAL(10, 2), nullable=False) # Positive for add, negative for deduct
    real_cost_associated_usd = Column(DECIMAL(10, 6), nullable=True)
    external_transaction_id = Column(String(255), nullable=True) # For Stripe, etc.
    description = Column(TEXT, nullable=True)
    created_at = Column(DateTime, default=func.now())
```
- **File:** `ai_dev_bot_platform/app/schemas/transaction.py`
- **Action:** Add the following `CreditTransaction` schemas:
```python
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import datetime
import uuid

class CreditTransactionBase(BaseModel):
    user_id: int
    project_id: Optional[uuid.UUID] = None
    api_key_usage_id: Optional[int] = None
    transaction_type: str
    credits_amount: Decimal
    real_cost_associated_usd: Optional[Decimal] = None
    external_transaction_id: Optional[str] = None
    description: Optional[str] = None

class CreditTransactionCreate(CreditTransactionBase):
    pass

class CreditTransactionInDB(CreditTransactionBase):
    id: int
    created_at: datetime.datetime
    class Config:
        from_attributes = True
```
- **Verification:** Model and schema files created. Table `credit_transactions` exists.

## Task 4: Create `ModelPricingService`
- **File:** `ai_dev_bot_platform/app/services/billing_service.py`
- **Action:** Add the following `ModelPricingService` class:
```python
from sqlalchemy.orm import Session
from app.models.api_key_models import ModelPricing # Path to your model
from app.schemas.api_key_schemas import ModelPricingCreate, ModelPricingUpdate # Path to your schema
from typing import Optional, List

class ModelPricingService:
    def get_pricing(self, db: Session, model_provider: str, model_name: str) -> Optional[ModelPricing]:
        return db.query(ModelPricing).filter(
            ModelPricing.model_provider == model_provider,
            ModelPricing.model_name == model_name,
            ModelPricing.is_active == True
        ).first()

    def create_pricing(self, db: Session, pricing_in: ModelPricingCreate) -> ModelPricing:
        db_pricing = ModelPricing(**pricing_in.model_dump())
        db.add(db_pricing)
        db.commit()
        db.refresh(db_pricing)
        return db_pricing
    
    # Add update, list methods if needed for admin
    # Note: Human needs to populate this table with actual pricing data.
```
- **Verification:** Service class and methods created.

## Task 5: Create `APIKeyUsageService`
- **File:** `ai_dev_bot_platform/app/services/billing_service.py`
- **Action:** Add the following `APIKeyUsageService` class:
```python
from app.models.api_key_models import APIKeyUsage
from app.schemas.api_key_schemas import APIKeyUsageCreate

class APIKeyUsageService:
    def log_usage(self, db: Session, usage_in: dict) -> APIKeyUsage:
        db_usage = APIKeyUsage(**usage_in)
        db.add(db_usage)
        db.commit()
        db.refresh(db_usage)
        return db_usage
    # Add methods to get usage if needed for reporting
```
- **Verification:** Service class and method created.

## Task 6: Create `CreditTransactionService`
- **File:** `ai_dev_bot_platform/app/services/billing_service.py`
- **Action:** Add the following `CreditTransactionService` class:
```python
from app.models.transaction import CreditTransaction # Path to your model
from app.schemas.transaction import CreditTransactionCreate # Path to your schema

class CreditTransactionService:
    def record_transaction(self, db: Session, transaction_in: dict) -> CreditTransaction:
        db_transaction = CreditTransaction(**transaction_in)
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    
    def get_transactions_for_user(self, db: Session, user_id: int) -> List[CreditTransaction]:
        return db.query(CreditTransaction).filter(CreditTransaction.user_id == user_id).order_by(CreditTransaction.created_at.desc()).all()
```
- **Verification:** Service class and methods created.

## Task 7: Enhance `LLMClient` to Return Token Counts and Model Info
- **File:** `ai_dev_bot_platform/app/utils/llm_client.py`
- **Action:** Modify `call_gemini` and `call_openrouter` to return a dictionary including `text_response`, `input_tokens`, `output_tokens`, `model_name_used`.
- **Verification:** Methods return the enhanced dictionary.

## Task 8: Implement Credit Deduction in `ModelOrchestrator`
- **File:** `ai_dev_bot_platform/app/services/orchestrator_service.py`
- **Action:** Implement credit deduction logic in `ModelOrchestrator`.
- **Verification:** Orchestrator attempts to deduct credits. Logs created in `api_key_usage` and `credit_transactions`. User credit balance updated.

## Task 9: Implement `/status` Command
- **File:** `ai_dev_bot_platform/app/telegram_bot/handlers.py`
- **Action:** Create `status_command` handler.
- **Verification:** `/status` command shows credit balance and basic project info.

## Task 10: Implement `/credits` Command (Stub for Purchase)
- **File:** `ai_dev_bot_platform/app/telegram_bot/handlers.py`
- **Action:** Create `credits_command` handler.
- **Verification:** `/credits` command shows balance and placeholder message.