import logging
from app.utils.llm_client import LLMClient
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ImplementerAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def implement_todo_item(self, todo_item: str, project_context: str, tech_stack: Dict[str, Any]) -> dict:
        logger.info(f"Implementer Agent: Implementing TODO: '{todo_item}'")
        tech_stack_str = ", ".join([f"{k}: {v}" for k, v in tech_stack.items()]) if tech_stack else "Not specified"
        system_prompt = f"""You are an expert software developer. Implement the following task in the specified tech stack.
Tech Stack: {tech_stack_str}
Project Context:
{project_context}

Instructions:
1. Generate only the code required for the task.
2. Do not include any explanations, markdown, or extra text.
3. If the task requires multiple files, generate them in the format: 
   ```filename.ext
   // code
   ```
4. If the task is unclear, make a best-effort implementation.
5. Use the tech stack exactly as specified.
"""
        model_name = "openrouter/auto"
        code_response = await self.llm_client.call_openrouter(
            model_name=model_name,
            prompt=todo_item,
            system_prompt=system_prompt
        )
        return {"raw_code_response": code_response}