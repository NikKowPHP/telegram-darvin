import logging
from sqlalchemy.orm import Session
from app.schemas.user import User
from app.agents.architect_agent import ArchitectAgent
from app.agents.implementer_agent import ImplementerAgent
from app.services.api_key_manager import APIKeyManager
from app.utils.llm_client import LLMClient
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ModelOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.api_key_manager = APIKeyManager()
        self.llm_client = LLMClient(self.api_key_manager)
        self.architect_agent = ArchitectAgent(self.llm_client)
        self.implementer_agent = ImplementerAgent(self.llm_client)

    async def process_user_request(self, user: User, user_input: str) -> str:
        logger.info(f"Orchestrator processing request for user {user.telegram_user_id}: '{user_input}'")

        # Basic routing logic
        if "plan" in user_input.lower() or "architect" in user_input.lower():
            response = await self.handle_architect_request(user_input)
        elif "implement" in user_input.lower() or "code" in user_input.lower():
            response = await self.handle_implementer_request(user_input)
        else:
            response = "I'm not sure how to handle that yet. Try 'plan' or 'implement'."

        # TODO: Deduct credits based on agent used and response complexity/tokens
        # user_service.update_user_credits(self.db, user.telegram_user_id, amount_to_deduct)

        return response

    async def handle_architect_request(self, user_input: str) -> str:
        project_title = "User Project"  # Placeholder
        result = await self.architect_agent.generate_initial_plan_and_docs(user_input, project_title)
        if "error" in result:
            return f"Architect Agent error: {result['error']}"
        return result.get("documentation", "No documentation generated")

    async def handle_implementer_request(self, user_input: str) -> str:
        project_context = "No project context available"  # Placeholder
        tech_stack = {}  # Placeholder
        result = await self.implementer_agent.implement_todo_item(user_input, project_context, tech_stack)
        return result.get("raw_code_response", "No code generated")

def get_orchestrator(db: Session) -> ModelOrchestrator:
    return ModelOrchestrator(db)