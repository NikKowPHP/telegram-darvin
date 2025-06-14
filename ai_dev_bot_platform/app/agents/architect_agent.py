import logging
from typing import Dict, Any
from app.utils.llm_client import LLMClient
from app.schemas.project import Project
from app.core.config import settings

logger = logging.getLogger(__name__)


class ArchitectAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def generate_initial_plan_and_docs(
        self, project_requirements: str, project_title: str
    ) -> dict:
        logger.info(f"Architect Agent: Generating plan for '{project_title}'")
        prompt = f"""You are an expert software architect. Based on the following project requirements for a project titled '{project_title}',
generate:
1. A brief technical overview/architecture document (Markdown)
2. A preliminary technology stack suggestion (list form)
3. A detailed TODO list in Markdown task list format (using '- [ ]' for each item) for a small LLM (4B model) to implement the project.

Project Requirements:
{project_requirements}

Output format should be structured clearly with headings for each section.
Start the TODO list with '### Implementation TODO List'"""

        llm_response_dict = await self.llm_client.call_llm(
            prompt=prompt, model_name=settings.ARCHITECT_MODEL
        )
        response_text = llm_response_dict.get("text_response", "")

        if response_text.startswith("Error:"):
            logger.error(f"Architect Agent: Error from LLM: {response_text}")
            return {"error": response_text}

        try:
            doc_content = response_text
            todo_list_md = ""
            tech_stack = {}

            if "### Implementation TODO List" in response_text:
                parts = response_text.split("### Implementation TODO List", 1)
                doc_content = parts[0].strip()
                todo_list_md = (
                    "### Implementation TODO List\n" + parts[1].strip()
                    if len(parts) > 1
                    else ""
                )

            return {
                "documentation": doc_content,
                "tech_stack_suggestion": tech_stack,  # NEW: Return the dict
                "todo_list_markdown": todo_list_md,
                "llm_call_details": llm_response_dict,
            }
        except Exception as e:
            logger.error(
                f"Architect Agent: Error parsing LLM response: {e}", exc_info=True
            )
            return {"error": "Failed to parse LLM response for plan."}

    async def verify_implementation_step(
        self, project: Project, code_snippet: str, relevant_docs: str, todo_item: str
    ) -> dict:
        logger.info(
            f"Architect Agent: Verifying step for project {project.id}: '{todo_item}'"
        )
        prompt = f"""You are an expert code reviewer and software architect.
Project Title: {project.title}
Project Description: {project.description}
Relevant Documentation/Architecture:
{relevant_docs}

The task was: '{todo_item}'
The implemented code is:
{code_snippet}

Does this code correctly implement the task according to the project context and best practices?
Provide feedback: 'APPROVED' or 'REJECTED: [detailed reasons and suggestions]'.
If REJECTED, suggest updates to the code or the TODO list."""

        llm_response_dict = await self.llm_client.call_llm(
            prompt=prompt, model_name=settings.VERIFICATION_MODEL
        )
        response_text = llm_response_dict.get("text_response", "")

        if response_text.startswith("Error:"):
            return {
                "status": "ERROR",
                "feedback": response_text,
                "llm_call_details": llm_response_dict,
            }

        if "APPROVED" in response_text.upper():
            return {
                "status": "APPROVED",
                "feedback": response_text,
                "llm_call_details": llm_response_dict,
            }
        else:
            return {
                "status": "REJECTED",
                "feedback": response_text,
                "llm_call_details": llm_response_dict,
            }

    async def generate_readme(self, project: Project) -> str:
        logger.info(f"Architect Agent: Generating README for project {project.id}")
        prompt = f"""You are an expert technical writer. Generate a comprehensive README.md for the project titled '{project.title}'.
Include these sections with appropriate content:
1. Overview - Brief description of the project
2. Features - List of main functionalities
3. Installation - Step-by-step setup instructions
4. Configuration - Environment variables and settings
5. Usage - How to run/use the application
6. API Documentation - If applicable
7. Contributing - Guidelines for contributors
8. License - Project license information

Project Description:
{project.description}

Additional Context:
{project.documentation}

Use proper Markdown formatting with clear section headers and organization."""

        llm_response_dict = await self.llm_client.call_llm(
            prompt=prompt, model_name=settings.ARCHITECT_MODEL
        )
        response_text = llm_response_dict.get("text_response", "")

        if response_text.startswith("Error:"):
            logger.error(f"Architect Agent: Error generating README: {response_text}")
            return f"# ERROR\n{response_text}"

        return response_text
