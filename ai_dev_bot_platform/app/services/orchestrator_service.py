import logging
import re
import uuid
import os
import subprocess
from typing import Optional
from sqlalchemy.orm import Session
from app.schemas.user import User
from app.services.api_key_manager import APIKeyManager
from app.utils.llm_client import LLMClient
from app.utils.file_utils import create_project_zip
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
from app.services.task_queue import TaskQueue
from app.services.notification_service import NotificationService
from app.schemas.project import ProjectCreate, ProjectUpdate
from app.core.config import settings
from decimal import Decimal
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import json

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
        self.task_queue = TaskQueue()
        self.notifier = NotificationService()

    def _is_long_running(self, user_input: str) -> bool:
        """Determine if a request should be processed asynchronously"""
        return self._is_new_project(user_input) or user_input.lower().startswith("implement task")

    async def process_user_request(self, user: User, user_input: str) -> dict:
        logger.info(
            f"Orchestrator processing request for user {user.telegram_user_id}: '{user_input}'"
        )

        # Check if project manifest exists, if not handoff to Architect for blueprint mode
        if not os.path.exists('project_manifest.json'):
            logger.info("Project manifest not found. Initializing blueprint mode...")
            try:
                result = subprocess.run(
                    ['roo', '-m', 'architect', '--command', 'create_blueprint'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                logger.info(f"Architect blueprint creation successful:\n{result.stdout}")
                return {
                    "text": "Project manifest not found. Initialized blueprint mode and handed off to Architect.",
                    "zip_buffer": None
                }
            except subprocess.CalledProcessError as e:
                logger.error(f"Architect blueprint creation failed with exit code {e.returncode}:\n{e.stderr}")
                return {
                    "text": f"Failed to initialize blueprint mode: {e.stderr}",
                    "zip_buffer": None
                }
            except FileNotFoundError as e:
                logger.error(f"Command not found: {e}")
                return {
                    "text": "Command not found. Please ensure the Architect agent is available.",
                    "zip_buffer": None
                }
            except Exception as e:
                logger.error(f"Unexpected error during Architect handoff: {e}")
                return {
                    "text": f"Unexpected error: {e}",
                    "zip_buffer": None
                }

        # Check for Developer handoff signal
        # Check for Developer handoff signal
        if os.path.exists('COMMIT_COMPLETE.md'):
            logger.info("Commit complete signal found. Handing off to Architect for verification...")
            try:
                # Read commit details from file
                with open('COMMIT_COMPLETE.md', 'r') as f:
                    commit_details = f.read()
                
                # Parse task description from commit details
                task_match = re.search(r'# Task Complete: (.*?)\n', commit_details)
                task_description = task_match.group(1) if task_match else "Unknown task"
                
                # Get project context (simplified for example)
                project_context = "Current project implementation"  # Would normally get from DB
                
                # Have Architect verify the implementation
                # Get the current project from DB (simplified example)
                # In real implementation we would parse project ID from commit_details
                sample_project = ProjectCreate(
                    title="Verification Project",
                    description="Temporary project for verification",
                    user_id=uuid.uuid4()
                )
                verification_result = await self.architect_agent.verify_implementation_step(
                    project=sample_project,
                    code_snippet=commit_details,
                    relevant_docs=project_context,
                    todo_item=task_description
                )
                
                # Remove the signal file
                os.remove('COMMIT_COMPLETE.md')
                
                if verification_result.get('status') == 'APPROVED':
                    return {
                        "text": f"Commit verified by Architect!\n\n{commit_details}\n\nFeedback: {verification_result.get('feedback', 'No feedback')}",
                        "zip_buffer": None,
                        "status": "verified"
                    }
                else:
                    return {
                        "text": f"Architect verification failed:\n{verification_result.get('feedback', 'No feedback')}",
                        "zip_buffer": None
                    }
                
            except Exception as e:
                logger.error(f"Error during Architect verification: {e}")
                return {
                    "text": f"Error during verification: {e}",
                    "zip_buffer": None
                }
        if self._is_long_running(user_input):
            await self.task_queue.add_task(
                lambda: self._handle_task_async(user, user_input)
            )
            return {
                "text": "Your request has been queued. You'll receive updates when processing starts.",
                "zip_buffer": None
            }

        # Check if this is a command to refine a file
        refine_match = re.match(
            r"refine file (.+) in project (.+) with instruction: (.+)",
            user_input,
            re.IGNORECASE | re.DOTALL,
        )
        if refine_match:
            file_path = refine_match.group(1).strip()
            project_id = refine_match.group(2).strip()
            instruction = refine_match.group(3).strip()
            return await self._handle_refine_request(
                user, project_id, file_path, instruction
            )

        # Basic routing logic for agent-specific requests
        if "plan" in user_input.lower() or "architect" in user_input.lower():
            return await self._handle_architect_request(user_input)
        elif "implement" in user_input.lower() or "code" in user_input.lower():
            return await self._handle_implementer_request(user_input)

        return {
            "text": "I'm not sure how to handle that yet. Try describing a project or 'implement task X of project Y'",
            "zip_buffer": None,
        }

    async def _handle_task_async(self, user: User, user_input: str):
        """Process a task asynchronously from the queue"""
        try:
            await self.notifier.send_update(user.telegram_user_id, "🚀 Processing started...")

            result = None
            # Check if this is a new project description
            if self._is_new_project(user_input):
                result = await self._handle_new_project(user, user_input)
            else:
                # Check if this is a command to implement a TODO item
                todo_match = re.match(
                    r"implement task (\d+) of project (.+)", user_input, re.IGNORECASE
                )
                if todo_match:
                    task_index = int(todo_match.group(1))
                    project_id = todo_match.group(2)
                    result = await self._handle_implement_task(user, project_id, task_index)

            if result:
                await self.notifier.send_update(user.telegram_user_id, "✅ Processing completed!")
                return result

        except Exception as e:
            logger.error(f"Error processing async task: {e}", exc_info=True)
            await self.notifier.send_update(
                user.telegram_user_id,
                f"❌ Processing failed: {str(e)}"
            )
            raise

    def _is_new_project(self, user_input: str) -> bool:
        """Heuristic to detect new project descriptions"""
        return len(user_input.split()) > 5 and not user_input.startswith(
            ("implement", "plan", "code")
        )

    async def _handle_new_project(self, user: User, description: str) -> dict:
        """Create new project and generate initial plan"""
        try:
            # Create project
            project_in = ProjectCreate(
                title=f"Project {uuid.uuid4().hex[:8]}",
                description=description,
                user_id=user.id,
            )
            project = self.project_service.create_project(
                self.db, project_in, user_id=user.id
            )

            self.storage_service.create_bucket(str(project.id))

            plan_result = await self.architect_agent.generate_initial_plan_and_docs(
                project_requirements=description, project_title=project.title
            )

            if "error" in plan_result:
                return {
                    "text": f"Error generating project plan: {plan_result['error']}",
                    "zip_buffer": None,
                    "reply_markup": None,
                    "project_id": None,
                }

            if "llm_call_details" in plan_result:
                await self._deduct_credits_for_llm_call(
                    user=user,
                    llm_response_data=plan_result["llm_call_details"],
                    task_type="planning",
                    project_id=project.id,
                )

            update_data = ProjectUpdate(
                status="planning",
                current_todo_markdown=plan_result.get("todo_list_markdown", ""),
                tech_stack=plan_result.get("tech_stack_suggestion", {}),
            )
            self.project_service.update_project(self.db, project.id, update_data)

            # Build the keyboard with a button for the first task
            keyboard = []
            todo_items = [
                line
                for line in plan_result.get("todo_list_markdown", "").split("\n")
                if line.strip().startswith(("- [ ]", "[ ]"))
            ]

            if todo_items:
                # The new, much shorter callback data string
                callback_data = "implement:1"
                button = [
                    InlineKeyboardButton(
                        "▶️ Implement Task 1", callback_data=callback_data
                    )
                ]
                keyboard.append(button)

            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
            todo_preview = "\n".join(
                plan_result.get("todo_list_markdown", "").split("\n")[:3]
            )

            return {
                "text": (
                    f"Project '{project.title}' ({project.id}) created!\n\n"
                    f"First tasks:\n{todo_preview}\n\n"
                    "Ready to start building?"
                ),
                "zip_buffer": None,
                "reply_markup": reply_markup,
                "project_id": str(project.id),  # Return the project ID
            }
        except Exception as e:
            logger.error(f"Unexpected error creating project: {e}", exc_info=True)
            return {
                "text": "Failed to create project due to an unexpected error. Please try again.",
                "zip_buffer": None,
                "reply_markup": None,
                "project_id": None,
            }

    async def _handle_implement_task(
        self, user: User, project_id: str, task_index: int
    ) -> str:
        """Implement a specific TODO item from a project"""

        try:

            if user.credit_balance < 1.0:
                return {
                    "text": "Your credit balance is too low to start a new task. Please /credits to top up.",
                    "zip_buffer": None,
                }

            project = self.project_service.get_project(self.db, uuid.UUID(project_id))
            if not project:
                return {"text": "Project not found", "zip_buffer": None}

            # 1. Corrected logic to find all incomplete task lines, handling formats like '- [ ]'
            todo_lines = [
                line
                for line in project.current_todo_markdown.split("\n")
                if line.strip().startswith(("[ ]", "- [ ]"))
            ]

            if task_index < 1 or task_index > len(todo_lines):
                return {
                    "text": f"Invalid task index. Please choose between 1 and {len(todo_lines)}",
                    "zip_buffer": None,
                }

            # 2. Get the original line of the task to be processed
            original_task_line = todo_lines[task_index - 1]

            # 3. Robustly extract the task description, removing the checkbox part
            match = re.search(r"\[\s*\]\s*(.*)", original_task_line)
            if not match:
                logger.error(
                    f"Could not parse task text from line: '{original_task_line}'"
                )
                return {
                    "text": "Internal error: could not parse the task from the TODO list.",
                    "zip_buffer": None,
                }
            todo_item = match.group(1).strip()

            # Generate code with implementer agent
            implementation = await self.implementer_agent.implement_todo_item(
                todo_item=todo_item,
                project_context=project.description,
                tech_stack=project.tech_stack or {},
                project_id=str(project.id),
                codebase_indexer=self.codebase_indexing_service,
            )

            if implementation.get("error"):
                return {
                    "text": f"Error implementing task: {implementation['error']}",
                    "zip_buffer": None,
                }

            # Deduct credits for LLM call if successful
            if "llm_call_details" in implementation:
                await self._deduct_credits_for_llm_call(
                    user=user,
                    llm_response_data=implementation["llm_call_details"],
                    task_type="implementation",
                    project_id=project.id,
                )

            # Store generated file
            if implementation["filename"] and implementation["code"]:
                self.project_file_service.create_project_file(
                    self.db,
                    project_id=project.id,
                    file_path=implementation["filename"],
                    content=implementation["code"],
                )

                # Also upload the new file to Supabase Storage
                self.storage_service.upload_file(
                    bucket_name=str(project.id),
                    file_path=implementation["filename"],
                    file_content=implementation["code"],
                )

                # Index the newly created/updated file
                await self.codebase_indexing_service.index_file_content(
                    project_id=str(project.id),  # Ensure project_id is string
                    file_path=implementation["filename"],
                    content=implementation["code"],
                )

            logger.info(
                f"Requesting verification for task: {todo_item} of project {project.id}"
            )

            # Prepare relevant docs for verification (simplified for now)
            relevant_docs_for_verification = project.description
            if project.current_todo_markdown:
                relevant_docs_for_verification += (
                    "\n\n## Current TODO Plan:\n" + project.current_todo_markdown
                )

            verification_result = await self.architect_agent.verify_implementation_step(
                project=project,
                code_snippet=implementation["code"],
                relevant_docs=relevant_docs_for_verification,
                todo_item=todo_item,
            )

            # Deduct credits for verification LLM call
            if "llm_call_details" in verification_result:
                await self._deduct_credits_for_llm_call(
                    user=user,
                    llm_response_data=verification_result["llm_call_details"],
                    task_type="verification",
                    project_id=project.id,
                )

            verification_status = verification_result.get("status", "ERROR")
            verification_feedback = verification_result.get(
                "feedback", "No feedback provided."
            )

            if verification_status == "APPROVED":
                # --- START OF FIX ---

                # 4. Mark TODO as complete by safely replacing the checkbox in the original line
                completed_task_line = original_task_line.replace("[ ]", "[x]", 1)
                new_todo_markdown = project.current_todo_markdown.replace(
                    original_task_line, completed_task_line, 1
                )

                # --- END OF FIX ---

                updated_project_status = "implementing"

                if "[ ]" not in new_todo_markdown:
                    updated_project_status = "verification_complete"
                    logger.info(f"All tasks completed for project {project.id}")

                    logger.info(
                        f"Project {project.id} tasks complete. Generating README.md..."
                    )
                    self.project_service.update_project(
                        self.db, project.id, ProjectUpdate(status="readme_generation")
                    )

                    bucket_name = str(project.id)
                    storage_files = self.storage_service.list_files(bucket_name)
                    project_files_for_readme = []
                    for storage_file in storage_files:
                        file_content = self.storage_service.download_file(
                            bucket_name, storage_file["name"]
                        )
                        if file_content is not None:
                            project_files_for_readme.append(
                                {
                                    "file_path": storage_file["name"],
                                    "content": file_content,
                                }
                            )

                    readme_content = await self.architect_agent.generate_readme(project)

                    if "Error" in readme_content:  # Simplified check
                        self.project_service.update_project(
                            self.db, project.id, ProjectUpdate(status="readme_failed")
                        )
                        return {
                            "text": f"All tasks implemented and verified, but failed to generate README.md: {readme_content}",
                            "zip_buffer": None,
                        }
                    else:
                        self.project_file_service.create_project_file(
                            db=self.db,
                            project_id=project.id,
                            file_path="README.md",
                            content=readme_content,
                        )
                        self.storage_service.upload_file(
                            bucket_name, "README.md", readme_content
                        )
                        self.project_service.update_project(
                            self.db,
                            project.id,
                            ProjectUpdate(
                                status="completed", completed_at=datetime.utcnow()
                            ),
                        )
                        logger.info(
                            f"README.md generated and project {project.id} marked as completed."
                        )

                        project_files_for_readme.append(
                            {"file_path": "README.md", "content": readme_content}
                        )
                        zip_buffer = create_project_zip(project_files_for_readme)

                        return {
                            "text": f"Project '{project.title}' is complete! All tasks implemented and verified. Project is ready for delivery.",
                            "zip_buffer": zip_buffer,
                            "project_title": project.title,
                        }

                self.project_service.update_project(
                    self.db,
                    project.id,
                    ProjectUpdate(
                        current_todo_markdown=new_todo_markdown,
                        status=updated_project_status,
                    ),
                )

                return {
                    "text": (
                        f"Task '{todo_item}' implemented AND VERIFIED!\n"
                        f"File: {implementation.get('filename', 'N/A')}\n"
                        f"Architect Feedback: {verification_feedback}\n"
                        f"Project status: {updated_project_status}. Next steps..."
                    ),
                    "zip_buffer": None,
                }
            elif verification_status == "REJECTED":
                self.project_service.update_project(
                    self.db, project.id, ProjectUpdate(status="awaiting_refinement")
                )
                feedback_message = (
                    f"Task '{todo_item}' was REJECTED by the Architect.\n\n"
                    f"**Feedback:**\n{verification_feedback}\n\n"
                    "To fix this, you can use the `refine` command. Example:\n"
                    f"`refine file {implementation.get('filename', 'path/to/your/file.py')} in project {project.id} with instruction: [Your instructions to fix the issue based on feedback]`"
                )
                return {"text": feedback_message, "zip_buffer": None}
            else:  # ERROR case
                return {
                    "text": (
                        f"Error during verification of task '{todo_item}'.\n"
                        f"Feedback: {verification_feedback}"
                    ),
                    "zip_buffer": None,
                }
        except Exception as e:
            logger.error(f"Error implementing task: {e}", exc_info=True)
            return {
                "text": "Failed to implement task. Please try again.",
                "zip_buffer": None,
            }

    async def _handle_architect_request(self, user_input: str) -> str:
        """Handle architect-specific requests with codebase context"""
        try:
            # Get relevant context from codebase index
            # For now, we'll use a placeholder project ID since we don't have a real project context
            project_id = "placeholder_project_id"
            context_results = await self.codebase_indexing_service.query_codebase(
                project_id, user_input
            )
            context = "\n".join(
                [f"{res['file_path']}:\n{res['content']}" for res in context_results]
            )

            return {
                "text": (
                    f"Architect Agent would handle: '{user_input}'\n"
                    f"Code context:\n{context}"
                ),
                "zip_buffer": None,
            }
        except Exception as e:
            logger.error(f"Error in architect request: {e}", exc_info=True)
            return {"text": "Error processing architect request.", "zip_buffer": None}

    async def _handle_refine_request(
        self, user: User, project_id: str, file_path: str, instruction: str
    ) -> dict:
        import os
        import tempfile

        logger.info(f"Refining file {file_path} for project {project_id}")
        project = self.project_service.get_project(self.db, uuid.UUID(project_id))
        if not project:
            return {"text": "Project not found", "zip_buffer": None}

        # Use the project ID as the bucket name (must be created in Supabase dashboard)
        bucket_name = str(project.id)

        # 1. Download file content from Supabase Storage
        original_content = self.storage_service.download_file(bucket_name, file_path)
        if original_content is None:
            return {
                "text": f"Could not find file '{file_path}' in project storage.",
                "zip_buffer": None,
            }

        with tempfile.TemporaryDirectory() as temp_dir:
            local_file_path = os.path.join(temp_dir, os.path.basename(file_path))

            # 2. Write file to temporary local disk for Aider
            with open(local_file_path, "w") as f:
                f.write(original_content)

            # 3. Run Aider on the local file
            aider_result = await self.implementer_agent.apply_changes_with_aider(
                project_root_path=temp_dir,
                files_to_edit=[os.path.basename(file_path)],
                instruction=instruction,
            )

            if aider_result["status"] == "success":
                # 4. Read the modified file
                with open(local_file_path, "r") as f:
                    new_content = f.read()

                # 5. Upload the new content back to Supabase Storage
                self.storage_service.upload_file(bucket_name, file_path, new_content)

                # 6. Update the content in the database as well
                db_file = self.project_file_service.get_file_by_path(
                    self.db, project.id, file_path
                )
                if db_file:
                    self.project_file_service.update_file_content(
                        self.db, db_file.id, new_content
                    )

                return {
                    "text": f"Successfully refined file '{file_path}'.",
                    "zip_buffer": None,
                }
            else:
                return {
                    "text": f"Failed to refine file '{file_path}'.\nError: {aider_result['output']}",
                    "zip_buffer": None,
                }

    async def _handle_implementer_request(self, user_input: str) -> str:
        """Handle implementer-specific requests with codebase context"""
        try:
            # Get relevant context from codebase index
            # For now, we'll use a placeholder project ID since we don't have a real project context
            project_id = "placeholder_project_id"
            context_results = await self.codebase_indexing_service.query_codebase(
                project_id, user_input
            )
            context = "\n".join(
                [f"{res['file_path']}:\n{res['content']}" for res in context_results]
            )

            return {
                "text": (
                    f"Implementer Agent would handle: '{user_input}'\n"
                    f"Code context:\n{context}"
                ),
                "zip_buffer": None,
            }
        except Exception as e:
            logger.error(f"Error in implementer request: {e}", exc_info=True)
            return {"text": "Error processing implementer request.", "zip_buffer": None}

    async def _deduct_credits_for_llm_call(
        self,
        user: User,
        llm_response_data: dict,
        task_type: str,
        project_id: Optional[uuid.UUID] = None,
    ):
        """Deduct credits based on LLM usage and log transaction"""
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
        credits_to_deduct = credits_to_deduct.quantize(
            Decimal("0.01")
        )  # Round to 2 decimal places

        if credits_to_deduct <= 0:  # No cost or negligible
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
            # Handle this scenario - maybe pause project, notify user
            # For now, log and proceed. This needs robust handling.
            return

        # Record credit transaction
        transaction = {
            "user_id": user.id,
            "project_id": project_id,
            "api_key_usage_id": api_usage_record.id,
            "transaction_type": "usage_deduction",
            "credits_amount": -credits_to_deduct,  # Negative for deduction
            "real_cost_associated_usd": actual_cost_usd,
            "description": f"Usage for {task_type} with {model_name_used}",
        }
        self.credit_transaction_service.record_transaction(self.db, transaction)
        logger.info(
            f"Deducted {credits_to_deduct} credits from user {user.id}. New balance: {updated_user.credit_balance}"
        )

# Function to get orchestrator instance
def get_orchestrator(db: Session) -> ModelOrchestrator:
    return ModelOrchestrator(db)
