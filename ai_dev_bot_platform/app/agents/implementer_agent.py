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

            # Step 6: Generate README
            readme_service = ReadmeGenerationService({
                "name": "AI Developer Bot Platform",
                "description": "Autonomous AI-powered development platform with TDD workflow"
            })
            readme_content = readme_service.generate_readme()
            with open(f"{project_root}/README.md", "w") as f:
                f.write(readme_content)
            
            # Commit the generated README
            subprocess.run(["git", "add", "README.md"], cwd=project_root, check=True)
            subprocess.run(["git", "commit", "-m", "docs: Add project README"], cwd=project_root, check=True)

            logger.info("TDD cycle and documentation completed successfully")
            return {"status": "success", "task": task_description}

    async def implement_todo_item(
        self,
        todo_item: str,
        project_context: str,
        tech_stack: Dict[str, Any],
        project_id: str,
        codebase_indexer: Any,
    ) -> dict:
        """Implement a TODO item using the TDD cycle."""
        logger.info(
            f"Implementer Agent: Implementing TODO: '{todo_item}' for project {project_id}"
        )

        # Run the TDD cycle with the todo_item as the task description
        result = await self.run_tdd_cycle(project_root=f"/home/kasjer/projects/{project_id}", task_description=todo_item)

        # Check if the TDD cycle was successful
        if result["status"] == "error":
            return {
                "error": f"TDD cycle failed for task: {todo_item}. Error: {result.get('error', 'Unknown error')}",
                "llm_call_details": {},
            }

        return {
            "status": "success",
            "task": todo_item,
            "message": "Task implemented successfully using TDD cycle",
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
