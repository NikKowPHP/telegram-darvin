from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)
import logging

logger = logging.getLogger(__name__)
from app.models.api_key_models import ModelPricing
from app.schemas.api_key_schemas import ModelPricingCreate, ModelPricingUpdate
from app.models.api_key_models import APIKeyUsage
from app.schemas.api_key_schemas import APIKeyUsageCreate
from app.models.transaction import CreditTransaction
from app.schemas.transaction import CreditTransactionCreate
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

class APIKeyUsageService:
    def log_usage(self, db: Session, usage_in: APIKeyUsageCreate) -> Optional[APIKeyUsage]:
        try:
            db_usage = APIKeyUsage(**usage_in.model_dump())
            db.add(db_usage)
            db.commit()
            db.refresh(db_usage)
            return db_usage
        except Exception as e:
            logger.error(f"Failed to log API key usage: {e}", exc_info=True)
            db.rollback()
            return None

class CreditTransactionService:
    def record_transaction(self, db: Session, transaction_in: CreditTransactionCreate) -> Optional[CreditTransaction]:
        try:
            db_transaction = CreditTransaction(**transaction_in.model_dump())
            db.add(db_transaction)
            db.commit()
            db.refresh(db_transaction)
            return db_transaction
        except Exception as e:
            logger.error(f"Failed to record credit transaction: {e}", exc_info=True)
            db.rollback()
            return None
    
    def get_transactions_for_user(self, db: Session, user_id: int) -> List[CreditTransaction]:
        return db.query(CreditTransaction).filter(CreditTransaction.user_id == user_id).order_by(CreditTransaction.created_at.desc()).all()