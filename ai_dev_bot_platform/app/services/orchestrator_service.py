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
from app.schemas.project import ProjectCreate, ProjectUpdate

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
                tech_stack=project.tech_stack or {}
            )
            
            if implementation.get("error"):
                return f"Error implementing task: {implementation['error']}"
            
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
            
            # Update TODO list to mark item as complete
            new_todo = project.current_todo_markdown.replace(
                f"[ ] {todo_item}", 
                f"[x] {todo_item}"
            )
            self.project_service.update_project(self.db, project.id, ProjectUpdate(
                current_todo_markdown=new_todo,
                status="implementing"
            ))
            
            return (
                f"Task {task_index} implemented!\n"
                f"File created: {implementation.get('filename', 'N/A')}\n"
                f"Next: Use 'implement task {task_index+1} of project {project.id}'"
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

# Function to get orchestrator instance
def get_orchestrator(db: Session) -> ModelOrchestrator:
    return ModelOrchestrator(db)