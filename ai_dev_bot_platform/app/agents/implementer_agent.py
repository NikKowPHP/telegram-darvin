import logging
import asyncio
import re
from app.utils.llm_client import LLMClient
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

VALID_FILENAME_REGEX = re.compile(r"^[a-zA-Z0-9_./-]+\.[a-zA-Z0-9]+$")


def is_valid_filename(filename: str) -> bool:
    """Checks if a string is a plausible filename."""
    if not filename or len(filename) > 255:
        return False
    # Check for obvious sentence-like structures or invalid characters
    if " " in filename.strip() or "\n" in filename or ":" in filename:
        return False
    # A simple check for file extension
    if "." not in filename.split("/")[-1]:
        return False
    return True


class ImplementerAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def implement_todo_item(
        self,
        todo_item: str,
        project_context: str,
        tech_stack: Dict[str, Any],
        project_id: str,
        codebase_indexer: Any,
    ) -> dict:
        logger.info(
            f"Implementer Agent: Implementing TODO: '{todo_item}' for project {project_id}"
        )
        tech_stack_str = (
            ", ".join([f"{k}: {v}" for k, v in tech_stack.items()])
            if tech_stack
            else "Not specified"
        )

        # Get relevant code context
        relevant_code = (
            "No specific relevant code snippets found in the current codebase."
        )
        if codebase_indexer:
            logger.debug(
                f"Implementer querying codebase for context related to: {todo_item}"
            )
            context_snippets = await codebase_indexer.query_codebase(
                project_id=project_id, query=todo_item, top_k=2
            )
            if context_snippets:
                relevant_code = "\n---\n".join(
                    [
                        f"File: {s['file_path']}\n```\n{s['content_chunk']}\n```"
                        for s in context_snippets
                    ]
                )

        system_prompt = f"""You are an expert, non-conversational file-generating AI. Your SOLE purpose is to generate the full content of a single file based on a given task.

Tech Stack: {tech_stack_str}
Project Context: {project_context}

**CRITICAL INSTRUCTIONS:**
1.  Your entire response will be for a SINGLE file.
2.  The VERY FIRST line of your output MUST be the relative file path (e.g., `src/components/Button.js`).
3.  The SECOND line MUST begin the raw code for that file.
4.  DO NOT include any other text, explanations, apologies, or conversational filler.
5.  ABSOLUTELY NO markdown formatting like ```python or ``` around the code.
6.  If you cannot complete the task or it is ambiguous, respond with only the single word: ERROR

**CORRECT Response Format Example:**
src/utils/helpers.py
def new_helper_function(param1, param2):
    # function logic here
    return param1 + param2

**INCORRECT Response Format Example (DO NOT DO THIS):**
Of course! Here is the file you requested:
```python
src/utils/helpers.py
def new_helper_function(param1, param2):
    # function logic here
    return param1 + param2

"""

        model_name = settings.IMPLEMENTER_MODEL
        llm_response_dict = await self.llm_client.call_openrouter(
            model_name=model_name, prompt=todo_item, system_prompt=system_prompt
        )
        code_response = llm_response_dict.get("text_response", "").strip()

        # --- START OF FIX ---
        # 2. Defensive parsing and validation of the LLM response
        if not code_response or code_response == "ERROR":
            logger.error(
                f"ImplementerAgent: LLM returned an error or empty response for task: {todo_item}"
            )
            return {
                "error": "The AI model could not generate a file for this task. The task may be too ambiguous or complex. Please try refining the TODO list.",
                "llm_call_details": llm_response_dict,
            }

        # Parse the response
        if "\n" not in code_response:
            # If there's no newline, it's likely a malformed response (e.g., just a filename, or just conversation)
            logger.warning(
                f"ImplementerAgent: LLM response has no newline, likely malformed. Response: '{code_response[:100]}...'"
            )
            return {
                "error": "AI returned a malformed response (not a file). Please try the task again or refine the plan.",
                "llm_call_details": llm_response_dict,
            }

        lines = code_response.split("\n", 1)
        filename = lines[0].strip()
        code_content = lines[1] if len(lines) > 1 else ""

        # Validate the parsed filename
        if not is_valid_filename(filename):
            logger.error(
                f"ImplementerAgent: LLM returned an invalid filename: '{filename}'. Full response: '{code_response[:200]}...'"
            )
            return {
                "error": f"The AI model generated an invalid file path: '{filename}'. This often happens if the AI becomes conversational. Please try the task again.",
                "llm_call_details": llm_response_dict,
            }

        return {
            "filename": filename,
            "code": code_content.strip(),
            "llm_call_details": llm_response_dict,
        }
        # --- END OF FIX ---


async def apply_changes_with_aider(
    self, project_root_path: str, files_to_edit: list[str], instruction: str
) -> Dict[str, str]:
    logger.info(f"Applying changes to {files_to_edit} with Aider: {instruction}")

    # Command structure: aider --yes --message "instruction" file1 file2 ...
    command = ["aider", "--yes", "--message", instruction] + files_to_edit

    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=project_root_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            logger.info(f"Aider command successful. Output: {stdout.decode()}")
            return {"status": "success", "output": stdout.decode()}
        else:
            logger.error(f"Aider command failed. Error: {stderr.decode()}")
            return {"status": "error", "output": stderr.decode()}
    except FileNotFoundError:
        logger.error(
            "Aider command not found. Is 'aider-chat' installed in the environment?"
        )
        return {"status": "error", "output": "Aider command not found."}
    except Exception as e:
        logger.error(f"Exception running Aider: {e}", exc_info=True)
        return {"status": "error", "output": str(e)}
