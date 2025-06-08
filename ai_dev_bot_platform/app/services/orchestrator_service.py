import logging
import re
import uuid
from sqlalchemy.orm import Session
from app.schemas.user import User
from app.services.api_key_manager import APIKeyManager
from app.utils.llm_client import LLMClient
from app.agents.architect_agent import ArchitectAgent
from app.agents.implementer_agent import ImplementerAgent
from app.services.project_service import ProjectService
from app.services.project_file_service import ProjectFileService
from app.services.codebase_indexing_service import CodebaseIndexingService
from app.services.billing_service import ModelPricingService, APIKeyUsageService, CreditTransactionService
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

    async def process_user_request(self, user: User, user_input: str) -> str:
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
        
        # Basic routing logic for agent-specific requests
        if "plan" in user_input.lower() or "architect" in user_input.lower():
            return await self._handle_architect_request(user_input)
        elif "implement" in user_input.lower() or "code" in user_input.lower():
            return await self._handle_implementer_request(user_input)
        
        return "I'm not sure how to handle that yet. Try describing a project or 'implement task X of project Y'."

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
            
            # Generate plan with architect agent
            plan_result = await self.architect_agent.generate_initial_plan_and_docs(
                project_requirements=description,
                project_title=project.title
            )
            
            if "error" in plan_result:
                return f"Error generating project plan: {plan_result['error']}"
            
            # Deduct credits for LLM call if successful
            if "llm_call_details" in plan_result:
                await self._deduct_credits_for_llm_call(
                    user=user,
                    llm_response_data=plan_result["llm_call_details"],
                    task_type="planning",
                    project_id=project.id
                )
            
            # Update project with generated artifacts
            update_data = ProjectUpdate(
                status="planning",
                current_todo_markdown=plan_result.get("todo_list_markdown", ""),
                tech_stack=plan_result.get("tech_stack_suggestion", {})
            )
            self.project_service.update_project(self.db, project.id, update_data)
            
            # Return summary to user
            todo_preview = "\n".join(plan_result.get("todo_list_markdown", "").split("\n")[:3])
            return (
                f"Project '{project.title}' created!\n"
                f"First tasks:\n{todo_preview}\n"
                f"Use 'implement task 1 of project {project.id}' to start."
            )
        except Exception as e:
            logger.error(f"Error creating project: {e}", exc_info=True)
            return "Failed to create project. Please try again."

    async def _handle_implement_task(self, user: User, project_id: str, task_index: int) -> str:
        """Implement a specific TODO item from a project"""
        try:
            project = self.project_service.get_project(self.db, uuid.UUID(project_id))
            if not project:
                return "Project not found"
            
            # Get the specific TODO item
            todo_items = [line for line in project.current_todo_markdown.split("\n") 
                         if line.startswith("[ ]")]
            
            if task_index < 1 or task_index > len(todo_items):
                return f"Invalid task index. Please choose between 1 and {len(todo_items)}"
            
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
                return f"Error implementing task: {implementation['error']}"
            
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
                
                self.project_service.update_project(self.db, project.id, ProjectUpdate(
                    current_todo_markdown=new_todo_markdown,
                    status=updated_project_status
                ))
                
                return (
                    f"Task '{todo_item}' implemented AND VERIFIED!\n"
                    f"File: {implementation.get('filename', 'N/A')}\n"
                    f"Architect Feedback: {verification_feedback}\n"
                    f"Project status: {updated_project_status}. Next steps..."
                )
            elif verification_status == "REJECTED":
                # Do not mark TODO as complete.
                # Potentially add architect's feedback as a new sub-task or comment in TODO
                # For now, just inform user.
                self.project_service.update_project(self.db, project.id, ProjectUpdate(status="awaiting_refinement"))
                return (
                    f"Task '{todo_item}' implemented but REJECTED by Architect.\n"
                    f"File: {implementation.get('filename', 'N/A')}\n"
                    f"Architect Feedback: {verification_feedback}\n"
                    f"Please review the feedback and consider refining the task or providing more details."
                )
            else: # ERROR case
                return (
                    f"Error during verification of task '{todo_item}'.\n"
                    f"Feedback: {verification_feedback}"
                )
        except Exception as e:
            logger.error(f"Error implementing task: {e}", exc_info=True)
            return "Failed to implement task. Please try again."

    async def _handle_architect_request(self, user_input: str) -> str:
        """Handle architect-specific requests with codebase context"""
        try:
            # Get relevant context from codebase index
            # For now, we'll use a placeholder project ID since we don't have a real project context
            project_id = "placeholder_project_id"
            context_results = await self.codebase_indexing_service.query_codebase(project_id, user_input)
            context = "\n".join([f"{res['file_path']}:\n{res['content']}" for res in context_results])
            
            return (
                f"Architect Agent would handle: '{user_input}'\n"
                f"Code context:\n{context}"
            )
        except Exception as e:
            logger.error(f"Error in architect request: {e}", exc_info=True)
            return "Error processing architect request."

    async def _handle_implementer_request(self, user_input: str) -> str:
        """Handle implementer-specific requests with codebase context"""
        try:
            # Get relevant context from codebase index
            # For now, we'll use a placeholder project ID since we don't have a real project context
            project_id = "placeholder_project_id"
            context_results = await self.codebase_indexing_service.query_codebase(project_id, user_input)
            context = "\n".join([f"{res['file_path']}:\n{res['content']}" for res in context_results])
            
            return (
                f"Implementer Agent would handle: '{user_input}'\n"
                f"Code context:\n{context}"
            )
        except Exception as e:
            logger.error(f"Error in implementer request: {e}", exc_info=True)
            return "Error processing implementer request."

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
        updated_user = update_user_credits(self.db, user.telegram_user_id, credits_to_deduct, is_deduction=True)
        
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