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

    # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: Implement generate_initial_plan_and_docs method
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
                    try:
                        if ":" in line:
                            category, items = line.split(":", 1)
                            category = category.strip().lower()
                            if category in tech_stack:
                                tech_stack[category] = [i.strip() for i in items.split(",") if i.strip()]
                    except Exception as e:
                        logger.warning(f"Failed to parse tech stack line: {line} - {str(e)}")

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
    # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: END
        except Exception as e:
            logger.error(
                f"Architect Agent: Error parsing LLM response: {e}", exc_info=True
            )
            return {"error": "Failed to parse LLM response for plan."}

    # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: Implement verify_implementation_step method
    async def verify_implementation_step(
        self, project: Project, code_snippet: str, relevant_docs: str, todo_item: str
    ) -> dict:
        """Verify a single implementation step against project requirements with detailed analysis"""
        logger.info(
            f"Architect Agent: Verifying implementation step for project {project.id}: '{todo_item}'"
        )
        
        # Build verification prompt with structured criteria
        prompt = architect_code_verification.PROMPT.format(
            project_title=project.title,
            project_description=project.description,
            relevant_docs=relevant_docs,
            todo_item=todo_item,
            code_snippet=code_snippet,
            quality_criteria="""
            - Functional correctness: Does the code correctly implement the requirement?
            - Code quality: Is the code clean, readable and maintainable?
            - Security: Are there any potential vulnerabilities?
            - Performance: Are there any obvious inefficiencies?
            - Error handling: Are exceptions properly handled?
            - Testing: Is there adequate test coverage?
            - Documentation: Is the code properly documented?
            """
        )

        llm_response_dict = await self.llm_client.call_llm(
            prompt=prompt,
            model_name=settings.VERIFICATION_MODEL,
            temperature=0.2  # More deterministic output for verification
        )
        
        response_text = llm_response_dict.get("text_response", "")
        analysis = {}

        # Parse structured response
        if "VERIFICATION REPORT:" in response_text:
            report_sections = response_text.split("VERIFICATION REPORT:")[1].split("\n\n")
            for section in report_sections:
                if ":" in section:
                    key, value = section.split(":", 1)
                    analysis[key.strip().lower()] = value.strip()

        # Determine verification status
        status = "REJECTED"
        if "overall_status" in analysis:
            if "approved" in analysis["overall_status"].lower():
                status = "APPROVED"
            elif "needs_revision" in analysis["overall_status"].lower():
                status = "NEEDS_REVISION"

        return {
            "status": status,
            "feedback": response_text,
            "analysis": analysis,
            "llm_call_details": llm_response_dict,
            "verification_criteria": {
                "functional_correctness": analysis.get("functional correctness", ""),
                "code_quality": analysis.get("code quality", ""),
                "security": analysis.get("security", ""),
                "performance": analysis.get("performance", ""),
                "error_handling": analysis.get("error handling", ""),
                "testing": analysis.get("testing", ""),
                "documentation": analysis.get("documentation", "")
            }
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

    # ROO-AUDIT-TAG :: feature-003-architectural-planning.md :: Implement generate_technical_documentation method
    async def generate_technical_documentation(self, project: Project) -> dict:
        """Generate comprehensive technical documentation for a project"""
        logger.info(f"Architect Agent: Generating technical docs for project {project.id}")
        
        prompt = architect_readme_generation.TECH_DOCS_PROMPT.format(
            project_title=project.title,
            project_description=project.description,
            tech_stack=project.tech_stack
        )
        
        llm_response_dict = await self.llm_client.call_llm(
            prompt=prompt, model_name=settings.ARCHITECT_MODEL
        )
        response_text = llm_response_dict.get("text_response", "")
        
        if response_text.startswith("Error:"):
            logger.error(f"Technical docs generation error: {response_text}", exc_info=True)
            return {"error": response_text}
            
        return {
            "technical_docs": response_text,
            "llm_call_details": llm_response_dict
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
    # ROO-AUDIT-TAG :: refactoring-epic-010-audit-fixes.md :: END
