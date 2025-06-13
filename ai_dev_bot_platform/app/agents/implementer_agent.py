import logging
import asyncio
from app.utils.llm_client import LLMClient
from typing import Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)


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

        system_prompt = f"""You are an expert software developer. Implement the following task in the specified tech stack.
Tech Stack: {tech_stack_str}
Project Context:
{project_context}

Relevant Code from Project:
{relevant_code}

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
        model_name = settings.IMPLEMENTER_MODEL
        llm_response_dict = await self.llm_client.call_openrouter(
            model_name=model_name, prompt=todo_item, system_prompt=system_prompt
        )
        code_response = llm_response_dict.get("text_response", "")
        filename = None
        code_content = ""
        if code_response and "\n" in code_response:
            try:
                lines = code_response.split("\n", 1)
                filename = lines[0].strip()
                if len(lines) > 1:
                    code_content = lines[1]
                else:  # Only filename was provided
                    code_content = ""
            except Exception as e:
                logger.error(f"ImplementerAgent: Error parsing filename and code: {e}")
                # Fallback if parsing fails, or return an error structure
                filename = "error_parsing_filename.txt"
                code_content = code_response  # return raw response as code
        elif code_response:  # No newline, assume it's all code or a filename only
            # This simple logic assumes if no newline, it might be a filename or just code.
            # For simplicity for 4B model, let's assume it's code without a clear filename.
            # A more robust solution would handle this better.
            filename = "unknown_file.txt"  # Default filename if only one line.
            code_content = code_response

        return {
            "filename": filename,
            "code": code_content.strip(),
            "llm_call_details": llm_response_dict,
        }

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
