# ROO-AUDIT-TAG :: plan-002-model-orchestrator.md :: Implement model orchestrator service
import logging
import uuid
import os
import asyncio
from typing import Optional
from sqlalchemy.orm import Session
from app.schemas.user import User
from app.services.api_key_manager import APIKeyManager
from app.utils.llm_client import LLMClient
from app.agents.architect_agent import ArchitectAgent
from app.agents.implementer_agent import ImplementerAgent
from app.services.project_service import ProjectService
from app.services.project_file_service import ProjectFileService
from app.services.codebase_indexing_service import CodebaseIndexingService
from app.services.billing_service import (
    ModelPricingService,
    APIKeyUsageService,
    CreditTransactionService
)
from app.services.user_service import UserService
from app.services.storage_service import StorageService
from app.services.notification_service import NotificationService
from app.schemas.project import ProjectUpdate
from app.core.config import settings
from decimal import Decimal

logger = logging.getLogger(__name__)

class ModelOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.api_key_manager = APIKeyManager()
        self.llm_client = LLMClient(self.api_key_manager)
        self.architect_agent = ArchitectAgent(self.llm_client)
        self.implementer_agent = ImplementerAgent(self.llm_client)
        self.project_service = ProjectService()
        self.project_file_service = ProjectFileService()
        self.codebase_indexing_service = CodebaseIndexingService(self.api_key_manager)
        self.model_pricing_service = ModelPricingService()
        self.api_key_usage_service = APIKeyUsageService()
        self.credit_transaction_service = CreditTransactionService()
        self.storage_service = StorageService()
        self.user_service = UserService()
        self.notifier = NotificationService()

    async def process_user_request(self, user: User, user_input: str) -> dict:
        """Main orchestration method that routes requests to appropriate agents"""
        logger.info(f"Processing request from user {user.id}: {user_input}")
        
        # Determine request type
        if "implement task" in user_input.lower():
            return await self._handle_implement_task(user, user_input)
        elif "refine file" in user_input.lower():
            return await self._handle_refine_file(user, user_input)
        else:
            return await self._handle_new_project(user, user_input)

    async def _handle_new_project(self, user: User, description: str) -> dict:
        """Handle new project creation workflow"""
        logger.info(f"Starting new project for user {user.id}")
        
        # Create project
        project = await self.project_service.create_project(
            self.db, 
            user.id,
            description
        )
        
        # Generate initial plan
        plan_result = await self.architect_agent.generate_initial_plan(
            project.description
        )
        
        # Update project with plan
        await self.project_service.update_project(
            self.db,
            project.id,
            {"current_todo_markdown": plan_result["todo_list"]}
        )
        
        return {
            "status": "success",
            "project_id": project.id,
            "todo_list": plan_result["todo_list"]
        }

    async def _handle_implement_task(self, user: User, command: str) -> dict:
        """Handle task implementation workflow"""
        logger.info(f"Implementing task for user {user.id}")
        
        # Parse task number from command
        task_num = int(command.split()[2])  # "implement task 1" -> 1
        
        # Get project and task
        project = await self._get_user_project(user)
        tasks = project.current_todo_markdown.split('\n')
        task = tasks[task_num - 1]  # 1-based to 0-based
        
        # Implement task
        result = await self.implementer_agent.implement_task(
            project.description,
            task,
            project.id
        )
        
        # Update project files
        for file_path, content in result["files"].items():
            await self.project_file_service.update_file(
                self.db,
                project.id,
                file_path,
                content
            )
            
        return {
            "status": "success",
            "files_updated": list(result["files"].keys())
        }

    async def _handle_refine_file(self, user: User, command: str) -> dict:
        """Handle file refinement workflow"""
        logger.info(f"Refining file for user {user.id}")
        
        # Parse file path from command
        file_path = command.split("refine file")[1].strip()
        
        # Get project and file content
        project = await self._get_user_project(user)
        file_content = await self.project_file_service.get_file(
            self.db,
            project.id,
            file_path
        )
        
        # Refine file
        result = await self.implementer_agent.refine_file(
            project.description,
            file_path, 
            file_content
        )
        
        # Update file
        await self.project_file_service.update_file(
            self.db,
            project.id,
            file_path,
            result["content"]
        )
        
        return {
            "status": "success",
            "file_path": file_path
        }

    async def _get_user_project(self, user: User):
        """Helper to get user's active project"""
        return await self.project_service.get_active_project(
            self.db,
            user.id
        )

def get_orchestrator(db: Session) -> ModelOrchestrator:
    return ModelOrchestrator(db)
# ROO-AUDIT-TAG :: plan-002-model-orchestrator.md :: END