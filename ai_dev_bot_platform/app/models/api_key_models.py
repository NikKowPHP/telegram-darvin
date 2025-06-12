from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, Boolean, TEXT, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from ai_dev_bot_platform.app.db.session import Base

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

class APIKeyUsage(Base):
    __tablename__ = "api_key_usage"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    api_key_identifier = Column(String(100), nullable=True)
    model_provider = Column(String(100), nullable=False)
    model_name = Column(String(255), nullable=False)
    task_type = Column(String(100), nullable=True)
    input_tokens_used = Column(Integer, default=0)
    output_tokens_used = Column(Integer, default=0)
    images_processed = Column(Integer, default=0)
    actual_cost_usd = Column(DECIMAL(10, 6), nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())