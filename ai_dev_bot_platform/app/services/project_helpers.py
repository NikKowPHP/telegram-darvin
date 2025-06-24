import logging
import uuid
import os
from typing import Optional
from sqlalchemy.orm import Session
from app.schemas.user import User
from app.services.api_key_manager import APIKeyManager
from app.utils.llm_client import LLMClient
from app.services.project_service import ProjectService
from app.services.project_file_service import ProjectFileService
from app.services.codebase_indexing_service import CodebaseIndexingService
from app.services.billing_service import (
    ModelPricingService,
    APIKeyUsageService,
    CreditTransactionService,
)
from app.services.user_service import UserService
from app.services.storage_service import StorageService
from app.services.notification_service import NotificationService
from app.schemas.project import ProjectUpdate
from app.core.config import settings
from decimal import Decimal

logger = logging.getLogger(__name__)


class ProjectHelpers:
    def __init__(self, db: Session):
        self.db = db
        self.api_key_manager = APIKeyManager()
        self.llm_client = LLMClient(self.api_key_manager)
        self.project_service = ProjectService()
        self.project_file_service = ProjectFileService()
        self.codebase_indexing_service = CodebaseIndexingService()
        self.model_pricing_service = ModelPricingService()
        self.api_key_usage_service = APIKeyUsageService()
        self.credit_transaction_service = CreditTransactionService()
        self.storage_service = StorageService()
        self.user_service = UserService()
        self.notifier = NotificationService()

    async def handle_new_project(self, user: User, description: str) -> dict:
        """Handle creation of new project"""
        try:
            project_in = ProjectCreate(
                title=f"Project {uuid.uuid4().hex[:8]}",
                description=description,
                user_id=user.id,
            )
            project = self.project_service.create_project(
                self.db, project_in, user_id=user.id
            )
            self.storage_service.create_bucket(str(project.id))
            return {"status": "success", "project_id": project.id}
        except Exception as e:
            logger.error(f"Error creating project: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    async def deduct_credits_for_llm_call(
        self,
        user: User,
        llm_response_data: dict,
        task_type: str,
        project_id: Optional[uuid.UUID] = None,
    ):
        """Deduct credits based on LLM usage"""
        model_provider = (
            "google"
            if "gemini" in llm_response_data.get("model_name_used", "").lower()
            else "openrouter"
        )
        model_name_used = llm_response_data.get("model_name_used")
        input_tokens = llm_response_data.get("input_tokens", 0)
        output_tokens = llm_response_data.get("output_tokens", 0)

        if not model_name_used:
            logger.error(
                f"Cannot deduct credits: model_name_used not found in LLM response data for user {user.id}"
            )
            return

        pricing = self.model_pricing_service.get_pricing(
            self.db, model_provider, model_name_used
        )
        if not pricing:
            logger.error(
                f"No pricing found for model {model_provider}/{model_name_used}. Cannot deduct credits for user {user.id}."
            )
            return

        actual_cost_usd = (
            Decimal(input_tokens) / Decimal(1000000)
        ) * pricing.input_cost_per_million_tokens + (
            Decimal(output_tokens) / Decimal(1000000)
        ) * pricing.output_cost_per_million_tokens

        # Log API usage
        usage_log = {
            "user_id": user.id,
            "project_id": project_id,
            "model_provider": model_provider,
            "model_name": model_name_used,
            "task_type": task_type,
            "input_tokens_used": input_tokens,
            "output_tokens_used": output_tokens,
            "actual_cost_usd": actual_cost_usd,
        }
        api_usage_record = self.api_key_usage_service.log_usage(self.db, usage_log)

        # Calculate credits to deduct
        credits_to_deduct = (
            actual_cost_usd / Decimal(str(settings.PLATFORM_CREDIT_VALUE_USD))
        ) * Decimal(str(settings.MARKUP_FACTOR))
        credits_to_deduct = credits_to_deduct.quantize(Decimal("0.01"))

        if credits_to_deduct <= 0:
            logger.info(
                f"Calculated credits to deduct is {credits_to_deduct} for user {user.id}. No deduction."
            )
            return

        # Deduct credits from user
        updated_user = self.user_service.update_user_credits(
            self.db, user.telegram_user_id, credits_to_deduct, is_deduction=True
        )

        if not updated_user:
            logger.warning(
                f"Failed to deduct {credits_to_deduct} credits for user {user.id} (insufficient balance or error)."
            )
            return

        # Record credit transaction
        transaction = {
            "user_id": user.id,
            "project_id": project_id,
            "api_key_usage_id": api_usage_record.id,
            "transaction_type": "usage_deduction",
            "credits_amount": -credits_to_deduct,
            "real_cost_associated_usd": actual_cost_usd,
            "description": f"Usage for {task_type} with {model_name_used}",
        }
        self.credit_transaction_service.record_transaction(self.db, transaction)
        logger.info(
            f"Deducted {credits_to_deduct} credits from user {user.id}. New balance: {updated_user.credit_balance}"
        )

    async def index_file_content(self, project_id: str, file_path: str, content: str):
        """Index file content in codebase"""
        return await self.codebase_indexing_service.index_file_content(
            db=self.db, project_id=project_id, file_path=file_path, content=content
        )

    async def upload_project_file(self, project_id: str, file_path: str, content: str):
        """Upload file to project storage"""
        self.storage_service.upload_file(
            bucket_name=project_id, file_path=file_path, file_content=content
        )
        return {"status": "success"}


def get_project_helpers(db: Session) -> ProjectHelpers:
    return ProjectHelpers(db)
