import logging
from typing import Dict, Any
from app.utils.llm_client import LLMClient
from app.schemas.project import Project
from app.core.config import settings
from app.prompts import (
    architect_initial_plan,
    architect_code_verification,
    architect_readme_generation,
    architect_architecture_validation,
)

logger = logging.getLogger(__name__)


class ArchitectAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def generate_initial_plan_and_docs(
        self, project_requirements: str, project_title: str
    ) -> dict:
        logger.info(f"Architect Agent: Generating plan for '{project_title}'")
        prompt = architect_initial_plan.PROMPT.format(
            project_title=project_title,
            project_requirements=project_requirements,
        )

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

            # Extract tech stack from response
            if "Technology Stack:" in response_text:
                tech_part = response_text.split("Technology Stack:", 1)[1].split(
                    "\n\n", 1
                )[0]
                tech_lines = [
                    line.strip() for line in tech_part.split("\n") if line.strip()
                ]
                tech_stack = {
                    "frontend": [],
                    "backend": [],
                    "database": [],
                    "infrastructure": [],
                }
                for line in tech_lines:
                    if ":" in line:
                        category, items = line.split(":", 1)
                        category = category.strip().lower()
                        if category in tech_stack:
                            tech_stack[category] = [i.strip() for i in items.split(",")]

            # Extract TODO list
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
                "tech_stack_suggestion": tech_stack,
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
        """Verify a single implementation step against project requirements"""
        logger.info(
            f"Architect Agent: Verifying step for project {project.id}: '{todo_item}'"
        )
        prompt = architect_code_verification.PROMPT.format(
            project_title=project.title,
            project_description=project.description,
            relevant_docs=relevant_docs,
            todo_item=todo_item,
            code_snippet=code_snippet,
        )

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

    async def validate_architecture(self, project: Project) -> dict:
        """Validate the overall project architecture"""
        prompt = architect_architecture_validation.PROMPT.format(
            project_title=project.title,
            project_description=project.description,
            tech_stack=project.tech_stack,
        )

        llm_response_dict = await self.llm_client.call_llm(
            prompt=prompt, model_name=settings.VERIFICATION_MODEL
        )
        return {
            "analysis": llm_response_dict.get("text_response", ""),
            "llm_call_details": llm_response_dict,
        }

    async def generate_readme(self, project: Project) -> str:
        logger.info(f"Architect Agent: Generating README for project {project.id}")

        # Collect metadata from project manifest
        tech_stack = project.tech_stack or {}
        dependencies = tech_stack.get("dependencies", [])
        env_vars = tech_stack.get("environment_variables", {})

        prompt = architect_readme_generation.PROMPT.format(
            project_title=project.title,
            dependencies=", ".join(dependencies) if dependencies else "None",
            env_vars=(
                ", ".join([f"{k}=[VALUE]" for k in env_vars.keys()])
                if env_vars
                else "None"
            ),
            project_description=project.description,
            documentation=project.documentation,
        )

        llm_response_dict = await self.llm_client.call_llm(
            prompt=prompt, model_name=settings.ARCHITECT_MODEL
        )
        response_text = llm_response_dict.get("text_response", "")

        if response_text.startswith("Error:"):
            logger.error(f"Architect Agent: Error generating README: {response_text}")
            return f"# ERROR\n{response_text}"

        return response_text
