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
1. Generate ONLY the code for the task.
2. The output should be for a SINGLE file.
3. Start your response with the filename on the VERY FIRST line (e.g., `my_new_file.py`).
4. On the NEXT line, begin the code content for that file.
5. Do NOT include any other explanations, markdown, or extra text. Just the filename and then the code.
Example:
src/utils/helper.py
def my_helper_function():
    pass
"""
        model_name = "openrouter/auto"
        code_response = await self.llm_client.call_openrouter(
            model_name=model_name,
            prompt=todo_item,
            system_prompt=system_prompt
        )
        filename = None
        code_content = ""
        if code_response and "\n" in code_response:
            try:
                lines = code_response.split("\n", 1)
                filename = lines[0].strip()
                if len(lines) > 1:
                    code_content = lines[1]
                else: # Only filename was provided
                    code_content = ""
            except Exception as e:
                logger.error(f"ImplementerAgent: Error parsing filename and code: {e}")
                # Fallback if parsing fails, or return an error structure
                filename = "error_parsing_filename.txt"
                code_content = code_response # return raw response as code
        elif code_response: # No newline, assume it's all code or a filename only
            # This simple logic assumes if no newline, it might be a filename or just code.
            # For simplicity for 4B model, let's assume it's code without a clear filename.
            # A more robust solution would handle this better.
            filename = "unknown_file.txt" # Default filename if only one line.
            code_content = code_response

        return {"filename": filename, "code": code_content.strip()}