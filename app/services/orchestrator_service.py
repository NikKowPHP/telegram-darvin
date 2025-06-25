# ROO-AUDIT-TAG :: feature-009-autonomous-loop.md :: Implement execute_autonomous_loop method
from typing import Optional
from pathlib import Path
from app.agents.implementer_agent import ImplementerAgent
from app.agents.architect_agent import ArchitectAgent
from app.utils.llm_client import LLMClient
from app.core.config import settings

class OrchestratorService:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.implementer = ImplementerAgent(llm_client)
        self.architect = ArchitectAgent(llm_client, None)  # Placeholder for CodebaseIndexingService

    def execute_autonomous_loop(self, project_id: str) -> None:
        """Execute the autonomous implementation loop for a project."""
        task_dir = Path(f"work_breakdown/tasks/")
        while True:
            next_task = self._get_next_task(task_dir)
            if not next_task:
                print("All tasks completed.")
                break
            
            print(f"Executing task: {next_task['description']} from {next_task['file_path']}")
            success = self.implementer.execute_task(next_task)
            
            if success:
                self._update_task_status(next_task['file_path'], next_task['line_number'], completed=True)
                print("Task completed successfully.")
            else:
                print("Task failed. Exiting autonomous loop.")
                break

    def _get_next_task(self, task_dir: Path) -> Optional[dict]:
        """Find the first incomplete task in the task directory."""
        # ROO-AUDIT-TAG :: feature-009-autonomous-loop.md :: Create helper _get_next_task
        for task_file in sorted(task_dir.glob("*.md")):
            with open(task_file, 'r') as f:
                for i, line in enumerate(f, 1):
                    if line.strip().startswith("- [ ]"):
                        return {
                            'file_path': str(task_file),
                            'line_number': i,
                            'description': line.strip()[5:].strip()
                        }
        return None

    def _update_task_status(self, file_path: str, line_number: int, completed: bool) -> None:
        """Update the task status in the markdown file."""
        # ROO-AUDIT-TAG :: feature-009-autonomous-loop.md :: Create helper _update_task_status
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        if 0 < line_number <= len(lines):
            lines[line_number-1] = lines[line_number-1].replace("[ ]", "[x]" if completed else "[ ]")
        
        with open(file_path, 'w') as f:
            f.writelines(lines)

# ROO-AUDIT-TAG :: feature-009-autonomous-loop.md :: END