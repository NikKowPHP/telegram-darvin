# Phase 5 Implementation Todo - Polish & README Generation

**Project Goal:** Enhance user experience with project READMEs, refine overall system stability, and prepare for testing.

## Task 1: Add `generate_project_readme` to `ArchitectAgent`
- [x] **File:** `ai_dev_bot_platform/app/agents/architect_agent.py`
- **Action:** Add a new method:
```python
from app.services.project_file_service import ProjectFileService
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class ArchitectAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    async def generate_initial_plan_and_docs(self, project_requirements: str, project_title: str) -> dict:
        # Existing code for generating initial plan and docs
        pass

    async def verify_implementation_step(self, project: Project, code_snippet: str, relevant_docs: str, todo_item: str) -> dict:
        # Existing code for verifying implementation steps
        pass

    async def generate_project_readme(self, project: Project, project_files_content: List[Dict[str,str]]) -> str: # project_files_content: [{"file_path": "...", "content": "..."}]
        logger.info(f"Architect Agent: Generating README.md for project {project.id} - {project.title}")
        
        all_files_summary = "\n\n".join([f"File: {f['file_path']}\n```\n{f['content'][:500]}...\n```" for f in project_files_content]) # Summarize file contents

        prompt = f"""
        You are an expert technical writer. For the software project titled '{project.title}', with the description:
        '{project.description}'
        And the following technology stack: {str(project.tech_stack)}
        And the following codebase structure and file snippets:
        {all_files_summary}

        Generate a comprehensive README.md file for this project. It should include:
        1. Project Title
        2. Brief Overview/Description
        3. Prerequisites (languages, frameworks, tools based on tech stack and code)
        4. Installation Steps (general steps like clone, install dependencies)
        5. Configuration Guide (if any environment variables or settings seem apparent from code/context)
        6. How to Run the Application (e.g., main script, server command)
        7. Key Features (derived from description and code)
        8. Basic Usage Examples (if applicable)
        
        The README should be well-formatted in Markdown.
        """
        # Use a capable model like Gemini Pro or a good OpenRouter model
        readme_content = await self.llm_client.call_gemini(prompt, model_name="gemini-1.5-pro-latest") # Or OpenRouter

        if readme_content.startswith("Error:"):
            logger.error(f"Error generating README for project {project.id}: {readme_content}")
            return f"Error: Could not generate README.md. LLM Error: {readme_content}"
        return readme_content
```
- **Verification:** Method exists.

## Task 2: Orchestrator Triggers `generate_project_readme`
- **File:** `ai_dev_bot_platform/app/services/orchestrator_service.py`
- **Action:**
  1.  In `_handle_implement_task`, when `updated_project_status` becomes `"verification_complete"`:
    ```python
    # ... inside if verification_status == "APPROVED":
    # ... inside if "[ ]" not in new_todo_markdown:
    # current status is "verification_complete"
    
    logger.info(f"Project {project.id} tasks complete. Generating README.md...")
    self.project_service.update_project(self.db, project.id, ProjectUpdate(status="readme_generation")) # New status

    # Fetch all project files
    db_project_files = self.project_file_service.get_project_files_by_project(self.db, project_id=project.id)
    project_files_for_readme = [{"file_path": pf.file_path, "content": pf.content} for pf in db_project_files]

    readme_content = await self.architect_agent.generate_project_readme(project, project_files_for_readme)

    if readme_content.startswith("Error:"):
        # Handle error, maybe set project status to 'readme_failed'
        self.project_service.update_project(self.db, project.id, ProjectUpdate(status="readme_failed"))
        # Return error message to user
        return f"All tasks implemented and verified, but failed to generate README.md: {readme_content}"
    else:
        # Save README.md as a project file
        self.project_file_service.create_project_file(
            db=self.db,
            project_id=project.id,
            file_path="README.md",
            content=readme_content,
            file_type="markdown"
        )
        self.project_service.update_project(self.db, project.id, ProjectUpdate(status="completed"))
        logger.info(f"README.md generated and project {project.id} marked as completed.")
        # TODO: Implement project packaging and delivery (Phase 5/6)
        return (
            f"Project '{project.title}' is complete! All tasks implemented and verified.\n"
            f"README.md has been generated. Project is ready for delivery (packaging TODO)."
        )
    ```
- **Verification:** Orchestrator calls `generate_project_readme` and saves the output.

## Task 3: Refine Error Handling in Services & Agents
- **Action:** Review all `*.py` files in `app/services/` and `app/agents/`.
    *   Wrap external calls (DB, LLM APIs) in more specific `try-except` blocks (e.g., `sqlalchemy.exc.SQLAlchemyError`, `httpx.HTTPStatusError`, specific Gemini/OpenRouter exceptions if their SDKs provide them).
    *   Log errors with detailed context (user_id, project_id, method name, parameters).
    *   Ensure functions/methods return clear error indicators or raise custom exceptions that can be caught by the orchestrator or handlers.
- **Verification:** At least 3 key services/agents have improved `try-except` blocks and contextual logging for errors.

## Task 4: Improve User-Facing Error Messages in Telegram Handlers
- **File:** `ai_dev_bot_platform/app/telegram_bot/handlers.py`
- **Action:** Review `except Exception as e:` blocks.
    *   Instead of generic "Sorry, something went wrong", provide slightly more specific but still user-friendly messages.
    *   Example: "Sorry, I couldn't process your request due to a problem with our AI services. Please try again later." or "An issue occurred with your project data. Our team has been notified."
    *   Avoid exposing raw exception details to the user.
- **Verification:** At least 2 error messages in handlers are more user-friendly.

## Task 5: Document Key Manual Test Scenarios (in `documentation/test_plan.md`)
- **File:** `documentation/test_plan.md`
- **Action:** Add a new section "6. High-Level Test Scenarios" (or similar).
    *   List 5-7 end-to-end scenarios. Examples:
        *   `TS-001: New User - Full Project Cycle (Simple Python App)`: /start -> describe project -> architect plan -> implement 2 tasks -> verification pass -> implement 1 task -> verification reject -> (manual refinement if UI allows, or assume new prompt) -> implement final task -> verification pass -> README generation -> project completion.
        *   `TS-002: User Runs Out of Credits During Project`: /start -> describe -> plan -> start implement -> credit deduction leads to insufficient -> bot pauses, informs user -> user (conceptually) adds credits -> bot resumes.
        *   `TS-003: LLM API Failure (Gemini)`: During planning, simulate Gemini API error -> Orchestrator handles, informs user.
        *   `TS-004: LLM API Failure (OpenRouter)`: During implementation, simulate OpenRouter API error -> Orchestrator handles, informs user.
        *   `TS-005: Invalid User Input`: User sends non-command text that doesn't fit project flow -> bot responds gracefully.
- **Verification:** Section and scenarios added to `test_plan.md`.