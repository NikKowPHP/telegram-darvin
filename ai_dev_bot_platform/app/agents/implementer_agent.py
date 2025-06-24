import logging
import asyncio
import re
import subprocess
from app.utils.llm_client import LLMClient
from typing import Dict, Any
from app.core.config import settings
from app.services.readme_generation_service import ReadmeGenerationService

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

    async def run_tdd_cycle(self, project_root: str, task_description: str):
        """Implement the feature for a given task and return the filename and code."""
        logger.info(f"Implementing task: {task_description}")

        # Implement the feature
        implementation_result = await self._implement_feature(
            project_root, task_description
        )
        if not implementation_result.get("success"):
            return implementation_result

        # Return only the filename and code
        return {
            "filename": implementation_result.get("filename", ""),
            "code": implementation_result.get("code", ""),
        }

    async def implement_todo_item(
        self,
        todo_item: str,
        project_context: str,
        tech_stack: Dict[str, Any],
        project_id: str,
        codebase_indexer: Any,
    ) -> dict:
        """Implement a TODO item and return the filename and code."""
        logger.info(f"Implementing TODO: '{todo_item}' for project {project_id}")

        try:
            # Get relevant context from codebase index
            relevant_code = await codebase_indexer.query_codebase(
                project_id=project_id, query=todo_item
            )

            # Build full context for implementation
            implementation_context = f"""
            Project Context: {project_context}
            Tech Stack: {tech_stack}
            Relevant Code: {relevant_code}
            Task: {todo_item}
            """

            # Run the implementation
            result = await self.run_tdd_cycle(
                project_root=f"/home/kasjer/projects/{project_id}",
                task_description=implementation_context,
            )

            if not result.get("success"):
                raise Exception(
                    result.get("error", "Unknown error during implementation")
                )

            # Validate the generated filename
            filename = result.get("filename", "")
            if not is_valid_filename(filename):
                raise Exception(f"Invalid filename generated: {filename}")

            return {
                "status": "success",
                "filename": filename,
                "code": result.get("code", ""),
                "context_used": implementation_context,
            }

        except Exception as e:
            logger.error(f"Failed to implement TODO item: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "todo_item": todo_item}

    async def apply_changes_with_aider(
        self,
        project_root_path: str,
        files_to_edit: list[str],
        instruction: str,
        max_retries: int = 3,
    ) -> Dict[str, str]:
        logger.info(f"Applying changes to {files_to_edit} with Aider: {instruction}")

        # Validate all files exist and are valid
        for file_path in files_to_edit:
            if not is_valid_filename(file_path):
                return {"status": "error", "output": f"Invalid filename: {file_path}"}
            if not os.path.exists(os.path.join(project_root_path, file_path)):
                return {"status": "error", "output": f"File not found: {file_path}"}

        # Command structure: aider --yes --message "instruction" file1 file2 ...
        command = ["aider", "--yes", "--message", instruction] + files_to_edit

        attempt = 0
        while attempt < max_retries:
            attempt += 1
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
                    return {
                        "status": "success",
                        "output": stdout.decode(),
                        "attempts": attempt,
                    }
                else:
                    logger.warning(
                        f"Aider attempt {attempt} failed. Error: {stderr.decode()}"
                    )
                    if attempt >= max_retries:
                        raise Exception(stderr.decode())
                    await asyncio.sleep(1)  # Brief delay before retry

            except FileNotFoundError:
                logger.error("Aider command not found. Is 'aider-chat' installed?")
                return {"status": "error", "output": "Aider command not found."}
            except Exception as e:
                logger.error(f"Exception running Aider: {e}", exc_info=True)
                if attempt >= max_retries:
                    return {"status": "error", "output": str(e), "attempts": attempt}

        return {
            "status": "error",
            "output": "Max retries exceeded",
            "attempts": max_retries,
        }
