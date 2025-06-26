import logging
import asyncio
import re
import subprocess
import os
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

    # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: Implement run_tdd_cycle method
    async def _implement_feature(self, project_root: str, task_description: str) -> dict:
        """Core implementation logic for a feature using TDD approach."""
        logger.info(f"Implementing feature: {task_description}")
        from app.services.codebase_indexing_service import CodebaseIndexer
        from app.utils.llm_client import LLMClient
        
        try:
            # Initialize required services
            llm_client = LLMClient()
            indexer = CodebaseIndexer(project_root)
            
            # Get relevant context from codebase
            relevant_code = await indexer.query_codebase(task_description)
            
            # Generate implementation prompt
            prompt = f"""Implement the following feature based on the project context:
            
            Feature Requirements:
            {task_description}
            
            Relevant Existing Code:
            {relevant_code}
            
            Please return only the code implementation in the correct language syntax.
            """
            
            # Get LLM response
            response = await llm_client.call_llm(
                prompt=prompt,
                model_name=settings.IMPLEMENTER_MODEL
            )
            
            # Extract filename from first line if specified
            code = response.get("text_response", "")
            filename = "implementation.py"  # default
            if code.startswith("# filename:"):
                filename_line, _, code = code.partition("\n")
                filename = filename_line.split(":")[1].strip()
            
            return {
                "success": True,
                "filename": filename,
                "code": code,
                "llm_response": response
            }
        except Exception as e:
            logger.error(f"Feature implementation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "task_description": task_description
            }

    async def run_tdd_cycle(self, project_root: str, task_description: str):
        """Implement a feature using Test-Driven Development approach."""
        logger.info(f"Starting TDD cycle for: {task_description}")
        from app.services.codebase_indexing_service import CodebaseIndexer
        from app.utils.llm_client import LLMClient
        
        try:
            llm_client = LLMClient()
            indexer = CodebaseIndexer(project_root)
            
            # 1. Generate test cases
            test_prompt = f"""Generate test cases for the following feature:
            {task_description}
            
            Please return the test code in the appropriate testing framework for the project.
            """
            test_response = await llm_client.call_llm(
                prompt=test_prompt,
                model_name=settings.IMPLEMENTER_MODEL
            )
            test_code = test_response.get("text_response", "")
            test_filename = "test_implementation.py"  # Could be extracted from response
            
            # 2. Implement the feature
            implementation_result = await self._implement_feature(
                project_root, task_description
            )
            if not implementation_result.get("success"):
                return implementation_result
                
            # 3. Validate implementation
            validation_prompt = f"""Verify the implementation against the test cases:
            Feature: {task_description}
            
            Implementation Code:
            {implementation_result['code']}
            
            Test Cases:
            {test_code}
            
            Does the implementation satisfy all test cases? Respond with only 'YES' or 'NO'.
            """
            validation_response = await llm_client.call_llm(
                prompt=validation_prompt,
                model_name=settings.VERIFICATION_MODEL
            )
            
            if "YES" not in validation_response.get("text_response", "").upper():
                return {
                    "success": False,
                    "error": "Implementation failed validation against test cases",
                    "test_code": test_code,
                    "implementation": implementation_result
                }
            
            # 4. Return comprehensive results
            return {
                "success": True,
                "filename": implementation_result.get("filename", ""),
                "code": implementation_result.get("code", ""),
                "test_filename": test_filename,
                "test_code": test_code,
                "validation_result": validation_response
            }
            
        except Exception as e:
            logger.error(f"TDD cycle failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "task_description": task_description
            }

    # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: Implement implement_todo_item method
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
        # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: END

        except Exception as e:
            logger.error(f"Failed to implement TODO item: {e}", exc_info=True)
            return {"status": "error", "error": str(e), "todo_item": todo_item}
        # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: END

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
