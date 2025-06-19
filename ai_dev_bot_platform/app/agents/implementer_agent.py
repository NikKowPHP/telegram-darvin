import logging
import asyncio
import re
import subprocess
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

    async def run_tdd_cycle(self, project_root: str, task_description: str):
        """Run a complete TDD cycle for a given task."""
        logger.info(f"Starting TDD cycle for task: {task_description}")

        try:
            # Step 1: Create current_task.md with the task breakdown
            task_file_path = f"{project_root}/current_task.md"
            with open(task_file_path, "w") as f:
                f.write(f"# Task: {task_description}\n\n## Steps:\n1. Implement feature\n2. Write tests\n3. Commit changes")

            # Step 2: Implement the feature
            logger.info("Implementing feature...")
            implementation_result = await self._implement_feature(project_root, task_description)
            if not implementation_result.get("success"):
                return implementation_result

            # Step 3: Write tests
            logger.info("Writing tests...")
            test_result = await self._write_tests(project_root, task_description)
            if not test_result.get("success"):
                return test_result

            # Step 4: Commit changes
            logger.info("Committing changes...")
            commit_result = await self._commit_changes(project_root, task_description)
            if not commit_result.get("success"):
                return commit_result

            # Step 5: Create COMMIT_COMPLETE.md signal file
            with open(f"{project_root}/COMMIT_COMPLETE.md", "w") as f:
                f.write(f"# Task Complete: {task_description}\n\nCommit message: {commit_result['commit_message']}")

            logger.info("TDD cycle completed successfully")
            return {"status": "success", "task": task_description}

        except Exception as e:
            logger.error(f"TDD cycle failed: {str(e)}", exc_info=True)
            return {"status": "error", "error": str(e)}

    async def _implement_feature(self, project_root: str, task_description: str) -> dict:
        """Implement the feature based on the task description."""
        # Implementation logic goes here
        return {"success": True}

    async def _write_tests(self, project_root: str, task_description: str) -> dict:
        """Write tests for the implemented feature."""
        # Test writing logic goes here
        return {"success": True}

    async def _commit_changes(self, project_root: str, task_description: str) -> dict:
        """Commit all changes with standardized message."""
        commit_message = f"feat: Complete task: {task_description}"
        try:
            subprocess.run(["git", "add", "."], cwd=project_root, check=True)
            subprocess.run(["git", "commit", "-m", commit_message], cwd=project_root, check=True)
            return {"success": True, "commit_message": commit_message}
        except subprocess.CalledProcessError as e:
            logger.error(f"Commit failed: {str(e)}")
            return {"success": False, "error": str(e)}
