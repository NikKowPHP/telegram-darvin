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
    def get_pricing(
        self, db: Session, model_provider: str, model_name: str
    ) -> Optional[ModelPricing]:
        return (
            db.query(ModelPricing)
            .filter(
                ModelPricing.model_provider == model_provider,
                ModelPricing.model_name == model_name,
                ModelPricing.is_active == True,
            )
            .first()
        )

    def create_pricing(
        self, db: Session, pricing_in: ModelPricingCreate
    ) -> ModelPricing:
        db_pricing = ModelPricing(**pricing_in.model_dump())
        db.add(db_pricing)
        db.commit()
        db.refresh(db_pricing)
        return db_pricing


class APIKeyUsageService:
    def log_usage(
        self, db: Session, usage_in: APIKeyUsageCreate
    ) -> Optional[APIKeyUsage]:
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
    def record_transaction(
        self, db: Session, transaction_in: CreditTransactionCreate
    ) -> Optional[CreditTransaction]:
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

    def get_transactions_for_user(
        self, db: Session, user_id: int
    ) -> List[CreditTransaction]:
        try:
            return (
                db.query(CreditTransaction)
                .filter(CreditTransaction.user_id == user_id)
                .order_by(CreditTransaction.created_at.desc())
                .all()
            )
        except SQLAlchemyError as e:
            logger.error(
                "Failed to get transactions for user",
                exc_info=True,
                extra={"user_id": user_id, "error": str(e)},
            )
            return []

    def process_credit_purchase(
        self,
        db: Session,
        user_id: int,
        amount: float,
        payment_method: str,
        payment_reference: str,
    ) -> CreditTransaction:
        """Process a new credit purchase"""
        try:
            transaction = CreditTransactionCreate(
                user_id=user_id,
                transaction_type="purchase",
                credits_amount=amount,
                payment_method=payment_method,
                payment_reference=payment_reference,
            )
            return self.record_transaction(db, transaction)
        except Exception as e:
            logger.error(f"Failed to process credit purchase: {e}", exc_info=True)
            raise

    def get_user_balance(self, db: Session, user_id: int) -> float:
        """Calculate current credit balance for a user"""
        try:
            credits = (
                db.query(func.sum(CreditTransaction.credits_amount))
                .filter(CreditTransaction.user_id == user_id)
                .scalar()
            )
            return credits or 0.0
        except Exception as e:
            logger.error(f"Failed to get user balance: {e}", exc_info=True)
            raise

    def deduct_credits(
        self, db: Session, user_id: int, amount: float, description: str
    ) -> CreditTransaction:
        """Deduct credits from user balance"""
        try:
            balance = self.get_user_balance(db, user_id)
            if balance < amount:
                raise ValueError("Insufficient credits")

            transaction = CreditTransactionCreate(
                user_id=user_id,
                transaction_type="usage",
                credits_amount=-amount,
                description=description,
            )
            return self.record_transaction(db, transaction)
        except Exception as e:
            logger.error(f"Failed to deduct credits: {e}", exc_info=True)
            raise

    def process_refund(
        self, db: Session, user_id: int, original_transaction_id: int, amount: float
    ) -> CreditTransaction:
        """Process a credit refund"""
        try:
            transaction = CreditTransactionCreate(
                user_id=user_id,
                transaction_type="refund",
                credits_amount=amount,
                related_transaction_id=original_transaction_id,
                description=f"Refund for transaction {original_transaction_id}",
            )
            return self.record_transaction(db, transaction)
        except Exception as e:
            logger.error(f"Failed to process refund: {e}", exc_info=True)
            raise
