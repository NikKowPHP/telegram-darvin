# ROO-AUDIT-TAG :: plan-002-model-orchestrator.md :: Implement model orchestrator service
import json
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
    CreditTransactionService,
)
from app.services.user_service import UserService
from app.services.storage_service import StorageService
from app.services.notification_service import NotificationService
from app.schemas.project import ProjectUpdate
from app.core.config import settings
from decimal import Decimal

logger = logging.getLogger(__name__)


class OrchestratorService:
    def __init__(self, db: Session):
        self.db = db
        self.api_key_manager = APIKeyManager()
        self.llm_client = LLMClient(self.api_key_manager)
        self.architect_agent = ArchitectAgent(self.llm_client)
        self.implementer_agent = ImplementerAgent(self.llm_client)
        self.project_service = ProjectService()
        self.project_file_service = ProjectFileService()
        self.codebase_indexing_service = CodebaseIndexingService()
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
            self.db, user.id, description
        )

        # Generate initial plan
        plan_result = await self.architect_agent.generate_initial_plan(
            project.description
        )

        # Update project with plan
        await self.project_service.update_project(
            self.db, project.id, {"current_todo_markdown": plan_result["todo_list"]}
        )

        return {
            "status": "success",
            "project_id": project.id,
            "todo_list": plan_result["todo_list"],
        }

    async def start_planning_phase(self, project_id: uuid.UUID, telegram_chat_id: int):
        """
        Takes an existing project and kicks off the architectural planning phase.
        Notifies the user on Telegram upon completion.
        """
        logger.info(f"Orchestrator: Starting planning phase for project {project_id}")
        try:
            # 1. Get the project from DB to ensure it exists and get its details
            project = self.project_service.get_project(self.db, project_id)
            if not project:
                logger.error(f"Planning phase failed: Project {project_id} not found.")
                await self.notifier.send_update(
                    telegram_chat_id,
                    f"Error: Could not find project {project_id}. Please start over.",
                )
                return

            # 2. Call Architect Agent to generate the plan, docs, and TODOs
            await self.notifier.send_update(
                telegram_chat_id,
                "🤖 The architect is thinking... This may take a moment.",
            )
            plan_result = await self.architect_agent.generate_initial_plan_and_docs(
                project_requirements=project.description,
                project_title=project.title,
            )

            if "error" in plan_result:
                error_msg = plan_result["error"]
                logger.error(
                    f"Architect agent failed for project {project_id}: {error_msg}"
                )
                await self.notifier.send_update(
                    telegram_chat_id,
                    f"Sorry, the architect ran into an issue: {error_msg}",
                )
                return

            # 3. Update the project in the database with the generated artifacts
            project_update_data = ProjectUpdate(
                status="planning_complete",
                tech_stack=plan_result.get("tech_stack_suggestion"),
                current_todo_markdown=plan_result.get("todo_list_markdown"),
                # Note: We could also save `plan_result.get("documentation")` to a new DB field
            )
            self.project_service.update_project(
                self.db, project_id, project_update_data
            )
            logger.info(f"Project {project_id} updated with initial plan.")

            # 4. Notify the user with the results
            response_message = (
                "✅ **Architect has finished!** Here is the initial plan:\n\n"
            )
            tech_stack_str = json.dumps(
                plan_result.get("tech_stack_suggestion", "Not specified"), indent=2
            )
            response_message += (
                f"**Technology Stack:**\n```json\n{tech_stack_str}\n```\n\n"
            )
            response_message += "**Next Steps (TODO List):**\n"
            response_message += plan_result.get(
                "todo_list_markdown", "No TODO list was generated."
            )

            # Telegram has a message size limit, so we might need to truncate or send multiple messages.
            # For now, we send one.
            if len(response_message) > 4000:
                response_message = (
                    response_message[:4000] + "\n\n... (message truncated)"
                )

            await self.notifier.send_update(telegram_chat_id, response_message)

        except Exception as e:
            logger.error(
                f"Critical error during planning phase for project {project_id}: {e}",
                exc_info=True,
            )
            await self.notifier.send_update(
                telegram_chat_id,
                "A critical error occurred during the planning phase. The team has been notified.",
            )

    # ROO-FIX-END

    async def _handle_implement_task(self, user: User, command: str) -> dict:
        """Handle task implementation workflow"""
        logger.info(f"Implementing task for user {user.id}")

        # Parse task number from command
        task_num = int(command.split()[2])  # "implement task 1" -> 1

        # Get project and task
        project = await self._get_user_project(user)
        tasks = project.current_todo_markdown.split("\n")
        task = tasks[task_num - 1]  # 1-based to 0-based

        # Implement task
        result = await self.implementer_agent.implement_task(
            project.description, task, project.id
        )

        # Update project files
        for file_path, content in result["files"].items():
            await self.project_file_service.update_file(
                self.db, project.id, file_path, content
            )

        return {"status": "success", "files_updated": list(result["files"].keys())}

    async def _handle_refine_file(self, user: User, command: str) -> dict:
        """Handle file refinement workflow"""
        logger.info(f"Refining file for user {user.id}")

        # Parse file path from command
        file_path = command.split("refine file")[1].strip()

        # Get project and file content
        project = await self._get_user_project(user)
        file_content = await self.project_file_service.get_file(
            self.db, project.id, file_path
        )

        # Refine file
        result = await self.implementer_agent.refine_file(
            project.description, file_path, file_content
        )

        # Update file
        await self.project_file_service.update_file(
            self.db, project.id, file_path, result["content"]
        )

        return {"status": "success", "file_path": file_path}

    async def _get_user_project(self, user: User):
        """Helper to get user's active project"""
        return await self.project_service.get_active_project(self.db, user.id)


def get_orchestrator_service(db: Session) -> OrchestratorService:
    return OrchestratorService(db)


# ROO-AUDIT-TAG :: plan-002-model-orchestrator.md :: END
