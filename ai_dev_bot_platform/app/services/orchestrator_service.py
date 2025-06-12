import logging
import re
import uuid
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
from app.services.billing_service import ModelPricingService, APIKeyUsageService, CreditTransactionService
from app.services.user_service import UserService
from app.services.storage_service import StorageService
from app.schemas.project import ProjectCreate, ProjectUpdate
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

    async def process_user_request(self, user: User, user_input: str) -> dict:
        logger.info(f"Orchestrator processing request for user {user.telegram_user_id}: '{user_input}'")

        # Check if this is a new project description
        if self._is_new_project(user_input):
            return await self._handle_new_project(user, user_input)
        
        # Check if this is a command to implement a TODO item
        todo_match = re.match(r"implement task (\d+) of project (.+)", user_input, re.IGNORECASE)
        if todo_match:
            task_index = int(todo_match.group(1))
            project_id = todo_match.group(2)
            return await self._handle_implement_task(user, project_id, task_index)
            
        # Check if this is a command to refine a file
        refine_match = re.match(r"refine file (.+) in project (.+) with instruction: (.+)", user_input, re.IGNORECASE | re.DOTALL)
        if refine_match:
            file_path = refine_match.group(1).strip()
            project_id = refine_match.group(2).strip()
            instruction = refine_match.group(3).strip()
            return await self._handle_refine_request(user, project_id, file_path, instruction)
        
        # Basic routing logic for agent-specific requests
        if "plan" in user_input.lower() or "architect" in user_input.lower():
            return await self._handle_architect_request(user_input)
        elif "implement" in user_input.lower() or "code" in user_input.lower():
            return await self._handle_implementer_request(user_input)
        
        return {'text': "I'm not sure how to handle that yet. Try describing a project or 'implement task X of project Y'", 'zip_buffer': None}

    def _is_new_project(self, user_input: str) -> bool:
        """Heuristic to detect new project descriptions"""
        return len(user_input.split()) > 5 and not user_input.startswith(("implement", "plan", "code"))

    async def _handle_new_project(self, user: User, description: str) -> str:
        """Create new project and generate initial plan"""
        try:
            # Create project
            project_in = ProjectCreate(
                title=f"Project {uuid.uuid4().hex[:8]}",
                description=description,
                user_id=user.id
            )
            project = self.project_service.create_project(self.db, project_in)
            
            # Create a dedicated storage bucket for this project
            self.storage_service.create_bucket(str(project.id))
            
            # Generate plan with architect agent
            try:
                plan_result = await self.architect_agent.generate_initial_plan_and_docs(
                    project_requirements=description,
                    project_title=project.title
                )
            except Exception as e:
                logger.error(f"LLM error generating project plan: {e}", exc_info=True)
                return {'text': f"Error generating project plan: {str(e)}", 'zip_buffer': None}
            
            if "error" in plan_result:
                return {'text': f"Error generating project plan: {plan_result['error']}", 'zip_buffer': None}
            
            # Deduct credits for LLM call if successful
            if "llm_call_details" in plan_result:
                try:
                    await self._deduct_credits_for_llm_call(
                        user=user,
                        llm_response_data=plan_result["llm_call_details"],
                        task_type="planning",
                        project_id=project.id
                    )
                except Exception as e:
                    logger.error(f"Credit deduction failed: {e}", exc_info=True)
                    # Continue despite credit deduction failure
            
            # Update project with generated artifacts
            try:
                update_data = ProjectUpdate(
                    status="planning",
                    current_todo_markdown=plan_result.get("todo_list_markdown", ""),
                    tech_stack=plan_result.get("tech_stack_suggestion", {})
                )
                self.project_service.update_project(self.db, project.id, update_data)
            except Exception as e:
                logger.error(f"Database update failed: {e}", exc_info=True)
                return {'text': "Failed to save project details. Please contact support.", 'zip_buffer': None}
            
            # Return summary to user
            todo_preview = "\n".join(plan_result.get("todo_list_markdown", "").split("\n")[:3])
            return {'text': (
                f"Project '{project.title}' created!\n"
                f"First tasks:\n{todo_preview}\n"
                f"Use 'implement task 1 of project {project.id}' to start."
            ), 'zip_buffer': None}
        except Exception as e:
            logger.error(f"Unexpected error creating project: {e}", exc_info=True)
            return {'text': "Failed to create project due to an unexpected error. Please try again.", 'zip_buffer': None}

    async def _handle_implement_task(self, user: User, project_id: str, task_index: int) -> str:
        """Implement a specific TODO item from a project"""
        try:
            # Add a pre-emptive check for credits before starting a task
            if user.credit_balance < 1.0: # A reasonable minimum threshold
                return {
                    'text': "Your credit balance is too low to start a new task. Please /credits to top up.",
                    'zip_buffer': None
                }
            
            project = self.project_service.get_project(self.db, uuid.UUID(project_id))
            if not project:
                return {'text': "Project not found", 'zip_buffer': None}
            
            # Get the specific TODO item
            todo_items = [line for line in project.current_todo_markdown.split("\n") 
                         if line.startswith("[ ]")]
            
            if task_index < 1 or task_index > len(todo_items):
                return {'text': f"Invalid task index. Please choose between 1 and {len(todo_items)}", 'zip_buffer': None}
            
            todo_item = todo_items[task_index - 1].replace("[ ]", "").strip()
            
            # Generate code with implementer agent
            implementation = await self.implementer_agent.implement_todo_item(
                todo_item=todo_item,
                project_context=project.description,
                tech_stack=project.tech_stack or {},
                project_id=str(project.id),
                codebase_indexer=self.codebase_indexing_service
            )
            
            if implementation.get("error"):
                return {'text': f"Error implementing task: {implementation['error']}", 'zip_buffer': None}
            
            # Deduct credits for LLM call if successful
            if "llm_call_details" in implementation:
                await self._deduct_credits_for_llm_call(
                    user=user,
                    llm_response_data=implementation["llm_call_details"],
                    task_type="implementation",
                    project_id=project.id
                )
            
            # Store generated file
            if implementation["filename"] and implementation["code"]:
                self.project_file_service.create_project_file(
                    self.db,
                    project_id=project.id,
                    file_path=implementation["filename"],
                    content=implementation["code"]
                )
                
                # Also upload the new file to Supabase Storage
                self.storage_service.upload_file(
                    bucket_name=str(project.id),
                    file_path=implementation["filename"],
                    file_content=implementation["code"]
                )
                
                # Index the newly created/updated file
                await self.codebase_indexing_service.index_file_content(
                    project_id=str(project.id), # Ensure project_id is string
                    file_path=implementation["filename"],
                    content=implementation["code"]
                )
            
            logger.info(f"Requesting verification for task: {todo_item} of project {project.id}")
            
            # Prepare relevant docs for verification (simplified for now)
            # In future, this could be specific design docs or related code.
            relevant_docs_for_verification = project.description # Or architect_agent's generated docs
            if project.current_todo_markdown: # Use the plan itself as part of context
                 relevant_docs_for_verification += "\n\n## Current TODO Plan:\n" + project.current_todo_markdown

            verification_result = await self.architect_agent.verify_implementation_step(
                project=project, # Pass the whole project object
                code_snippet=implementation["code"],
                relevant_docs=relevant_docs_for_verification,
                todo_item=todo_item
            )

            # Deduct credits for verification LLM call
            if "llm_call_details" in verification_result:
                await self._deduct_credits_for_llm_call(
                    user=user,
                    llm_response_data=verification_result["llm_call_details"],
                    task_type="verification",
                    project_id=project.id
                )

            verification_status = verification_result.get("status", "ERROR")
            verification_feedback = verification_result.get("feedback", "No feedback provided.")

            if verification_status == "APPROVED":
                # Mark TODO item as [x]
                new_todo_markdown = project.current_todo_markdown.replace(f"[ ] {todo_item}", f"[x] {todo_item}", 1)
                updated_project_status = "implementing" # Or "verifying_next_task"
                
                # Check if all tasks are done
                if "[ ]" not in new_todo_markdown:
                    updated_project_status = "verification_complete" # A new status before final README
                    logger.info(f"All tasks completed for project {project.id}")
                
                    logger.info(f"Project {project.id} tasks complete. Generating README.md...")
                    self.project_service.update_project(self.db, project.id, ProjectUpdate(status="readme_generation")) # New status

                    # Fetch all project files from Supabase Storage
                    bucket_name = str(project.id)
                    storage_files = self.storage_service.list_files(bucket_name)
                    project_files_for_readme = []
                    for storage_file in storage_files:
                        file_content = self.storage_service.download_file(bucket_name, storage_file['name'])
                        if file_content is not None:
                            project_files_for_readme.append({"file_path": storage_file['name'], "content": file_content})

                    readme_content = await self.architect_agent.generate_project_readme(project, project_files_for_readme)

                    if readme_content.startswith("Error:"):
                        # Handle error, maybe set project status to 'readme_failed'
                        self.project_service.update_project(self.db, project.id, ProjectUpdate(status="readme_failed"))
                        # Return error message to user
                        return {'text': f"All tasks implemented and verified, but failed to generate README.md: {readme_content}", 'zip_buffer': None}
                    else:
                        # Save README.md as a project file
                        self.project_file_service.create_project_file(
                            db=self.db,
                            project_id=project.id,
                            file_path="README.md",
                            content=readme_content,
                            file_type="markdown"
                        )
                        self.project_service.update_project(self.db, project.id, ProjectUpdate(status="completed"))
                        logger.info(f"README.md generated and project {project.id} marked as completed.")
                        # Create ZIP file of the project
                        zip_buffer = create_project_zip(project_files_for_readme)
                        
                        return {
                            'text': (
                            f"Project '{project.title}' is complete! All tasks implemented and verified.\n"
                            f"README.md has been generated. Project is ready for delivery."
                            ),
                            'zip_buffer': zip_buffer,
                            'project_title': project.title
                        }
                
                    logger.info(f"Project {project.id} tasks complete. Generating README.md...")
                    self.project_service.update_project(self.db, project.id, ProjectUpdate(status="readme_generation")) # New status

                    # Fetch all project files from Supabase Storage
                    bucket_name = str(project.id)
                    storage_files = self.storage_service.list_files(bucket_name)
                    project_files_for_readme = []
                    for storage_file in storage_files:
                        file_content = self.storage_service.download_file(bucket_name, storage_file['name'])
                        if file_content is not None:
                            project_files_for_readme.append({"file_path": storage_file['name'], "content": file_content})

                    readme_content = await self.architect_agent.generate_project_readme(project, project_files_for_readme)

                    if readme_content.startswith("Error:"):
                        # Handle error, maybe set project status to 'readme_failed'
                        self.project_service.update_project(self.db, project.id, ProjectUpdate(status="readme_failed"))
                        # Return error message to user
                        return {'text': f"All tasks implemented and verified, but failed to generate README.md: {readme_content}", 'zip_buffer': None}
                    else:
                        # Save README.md as a project file
                        self.project_file_service.create_project_file(
                            db=self.db,
                            project_id=project.id,
                            file_path="README.md",
                            content=readme_content,
                            file_type="markdown"
                        )
                        self.project_service.update_project(self.db, project.id, ProjectUpdate(status="completed"))
                        logger.info(f"README.md generated and project {project.id} marked as completed.")
                        # Create ZIP file of the project
                        zip_buffer = create_project_zip(project_files_for_readme)
                        
                        return {
                            'text': (
                            f"Project '{project.title}' is complete! All tasks implemented and verified.\n"
                            f"README.md has been generated. Project is ready for delivery."
                            ),
                            'zip_buffer': zip_buffer,
                            'project_title': project.title
                        }
                
                self.project_service.update_project(self.db, project.id, ProjectUpdate(
                    current_todo_markdown=new_todo_markdown,
                    status=updated_project_status
                ))
                
                return {'text': (
                    f"Task '{todo_item}' implemented AND VERIFIED!\n"
                    f"File: {implementation.get('filename', 'N/A')}\n"
                    f"Architect Feedback: {verification_feedback}\n"
                    f"Project status: {updated_project_status}. Next steps..."
                ), 'zip_buffer': None}
            elif verification_status == "REJECTED":
                # Do not mark TODO as complete. Provide clear instructions for refinement.
                self.project_service.update_project(self.db, project.id, ProjectUpdate(status="awaiting_refinement"))
                feedback_message = (
                    f"Task '{todo_item}' was REJECTED by the Architect.\n\n"
                    f"**Feedback:**\n{verification_feedback}\n\n"
                    "To fix this, you can use the `refine` command. Example:\n"
                    f"`refine file {implementation.get('filename', 'path/to/your/file.py')} in project {project.id} with instruction: [Your instructions to fix the issue based on feedback]`"
                )
                return {'text': feedback_message, 'zip_buffer': None}
            else: # ERROR case
                return {'text': (
                    f"Error during verification of task '{todo_item}'.\n"
                    f"Feedback: {verification_feedback}"
                ), 'zip_buffer': None}
        except Exception as e:
            logger.error(f"Error implementing task: {e}", exc_info=True)
            return {'text': "Failed to implement task. Please try again.", 'zip_buffer': None}

    async def _handle_architect_request(self, user_input: str) -> str:
        """Handle architect-specific requests with codebase context"""
        try:
            # Get relevant context from codebase index
            # For now, we'll use a placeholder project ID since we don't have a real project context
            project_id = "placeholder_project_id"
            context_results = await self.codebase_indexing_service.query_codebase(project_id, user_input)
            context = "\n".join([f"{res['file_path']}:\n{res['content']}" for res in context_results])
            
            return {'text': (
                f"Architect Agent would handle: '{user_input}'\n"
                f"Code context:\n{context}"
            ), 'zip_buffer': None}
        except Exception as e:
            logger.error(f"Error in architect request: {e}", exc_info=True)
            return {'text': "Error processing architect request.", 'zip_buffer': None}

    async def _handle_refine_request(self, user: User, project_id: str, file_path: str, instruction: str) -> dict:
        import os
        import tempfile
        
        logger.info(f"Refining file {file_path} for project {project_id}")
        project = self.project_service.get_project(self.db, uuid.UUID(project_id))
        if not project:
            return {'text': "Project not found", 'zip_buffer': None}

        # Use the project ID as the bucket name (must be created in Supabase dashboard)
        bucket_name = str(project.id)
        
        # 1. Download file content from Supabase Storage
        original_content = self.storage_service.download_file(bucket_name, file_path)
        if original_content is None:
            return {'text': f"Could not find file '{file_path}' in project storage.", 'zip_buffer': None}

        with tempfile.TemporaryDirectory() as temp_dir:
            local_file_path = os.path.join(temp_dir, os.path.basename(file_path))
            
            # 2. Write file to temporary local disk for Aider
            with open(local_file_path, "w") as f:
                f.write(original_content)

            # 3. Run Aider on the local file
            aider_result = await self.implementer_agent.apply_changes_with_aider(
                project_root_path=temp_dir,
                files_to_edit=[os.path.basename(file_path)],
                instruction=instruction
            )
            
            if aider_result["status"] == "success":
                # 4. Read the modified file
                with open(local_file_path, "r") as f:
                    new_content = f.read()

                # 5. Upload the new content back to Supabase Storage
                self.storage_service.upload_file(bucket_name, file_path, new_content)

                # 6. Update the content in the database as well
                db_file = self.project_file_service.get_file_by_path(self.db, project.id, file_path)
                if db_file:
                    self.project_file_service.update_file_content(self.db, db_file.id, new_content)

                return {'text': f"Successfully refined file '{file_path}'.", 'zip_buffer': None}
            else:
                return {'text': f"Failed to refine file '{file_path}'.\nError: {aider_result['output']}", 'zip_buffer': None}

    async def _handle_implementer_request(self, user_input: str) -> str:
        """Handle implementer-specific requests with codebase context"""
        try:
            # Get relevant context from codebase index
            # For now, we'll use a placeholder project ID since we don't have a real project context
            project_id = "placeholder_project_id"
            context_results = await self.codebase_indexing_service.query_codebase(project_id, user_input)
            context = "\n".join([f"{res['file_path']}:\n{res['content']}" for res in context_results])
            
            return {'text': (
                f"Implementer Agent would handle: '{user_input}'\n"
                f"Code context:\n{context}"
            ), 'zip_buffer': None}
        except Exception as e:
            logger.error(f"Error in implementer request: {e}", exc_info=True)
            return {'text': "Error processing implementer request.", 'zip_buffer': None}

    async def _deduct_credits_for_llm_call(
        self,
        user: User,
        llm_response_data: dict,
        task_type: str,
        project_id: Optional[uuid.UUID] = None
    ):
        """Deduct credits based on LLM usage and log transaction"""
        model_provider = "google" if "gemini" in llm_response_data.get("model_name_used", "").lower() else "openrouter"
        model_name_used = llm_response_data.get("model_name_used")
        input_tokens = llm_response_data.get("input_tokens", 0)
        output_tokens = llm_response_data.get("output_tokens", 0)

        if not model_name_used:
            logger.error(f"Cannot deduct credits: model_name_used not found in LLM response data for user {user.id}")
            return

        pricing = self.model_pricing_service.get_pricing(self.db, model_provider, model_name_used)
        if not pricing:
            logger.error(f"No pricing found for model {model_provider}/{model_name_used}. Cannot deduct credits for user {user.id}.")
            return

        actual_cost_usd = (
            (Decimal(input_tokens) / Decimal(1000000)) * pricing.input_cost_per_million_tokens +
            (Decimal(output_tokens) / Decimal(1000000)) * pricing.output_cost_per_million_tokens
        )
        
        # Log API usage
        usage_log = {
            "user_id": user.id,
            "project_id": project_id,
            "model_provider": model_provider,
            "model_name": model_name_used,
            "task_type": task_type,
            "input_tokens_used": input_tokens,
            "output_tokens_used": output_tokens,
            "actual_cost_usd": actual_cost_usd
        }
        api_usage_record = self.api_key_usage_service.log_usage(self.db, usage_log)

        # Calculate credits to deduct
        credits_to_deduct = (actual_cost_usd / Decimal(str(settings.PLATFORM_CREDIT_VALUE_USD))) * Decimal(str(settings.MARKUP_FACTOR))
        credits_to_deduct = credits_to_deduct.quantize(Decimal("0.01")) # Round to 2 decimal places

        if credits_to_deduct <= 0: # No cost or negligible
            logger.info(f"Calculated credits to deduct is {credits_to_deduct} for user {user.id}. No deduction.")
            return

        # Deduct credits from user
        updated_user = self.user_service.update_user_credits(self.db, user.telegram_user_id, credits_to_deduct, is_deduction=True)
        
        if not updated_user:
            logger.warning(f"Failed to deduct {credits_to_deduct} credits for user {user.id} (insufficient balance or error).")
            # Handle this scenario - maybe pause project, notify user
            # For now, log and proceed. This needs robust handling.
            return
        
        # Record credit transaction
        transaction = {
            "user_id": user.id,
            "project_id": project_id,
            "api_key_usage_id": api_usage_record.id,
            "transaction_type": "usage_deduction",
            "credits_amount": -credits_to_deduct, # Negative for deduction
            "real_cost_associated_usd": actual_cost_usd,
            "description": f"Usage for {task_type} with {model_name_used}"
        }
        self.credit_transaction_service.record_transaction(self.db, transaction)
        logger.info(f"Deducted {credits_to_deduct} credits from user {user.id}. New balance: {updated_user.credit_balance}")

# Function to get orchestrator instance
def get_orchestrator(db: Session) -> ModelOrchestrator:
    return ModelOrchestrator(db)