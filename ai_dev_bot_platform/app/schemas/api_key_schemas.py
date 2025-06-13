from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
import datetime
import uuid


class ModelPricingBase(BaseModel):
    model_provider: str
    model_name: str
    input_cost_per_million_tokens: Decimal
    output_cost_per_million_tokens: Decimal
    image_input_cost_per_image: Optional[Decimal] = None
    image_output_cost_per_image: Optional[Decimal] = None
    currency: str = "USD"
    notes: Optional[str] = None
    is_active: bool = True


class ModelPricingCreate(ModelPricingBase):
    pass


class ModelPricingUpdate(BaseModel):  # Allow partial updates
    input_cost_per_million_tokens: Optional[Decimal] = None
    output_cost_per_million_tokens: Optional[Decimal] = None
    image_input_cost_per_image: Optional[Decimal] = None
    image_output_cost_per_image: Optional[Decimal] = None
    currency: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ModelPricingInDB(ModelPricingBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


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
    pass


class APIKeyUsageInDB(APIKeyUsageBase):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True
