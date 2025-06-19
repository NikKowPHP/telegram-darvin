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
        
        # Collect metadata from project manifest
        tech_stack = project.tech_stack or {}
        dependencies = tech_stack.get('dependencies', [])
        env_vars = tech_stack.get('environment_variables', {})
        
        prompt = f"""You are an expert technical writer. Generate a comprehensive README.md for the project titled '{project.title}'.
Include these REQUIRED sections with appropriate content:

## Table of Contents
- Quick navigation links to all sections

## Overview
- Brief description of the project
- Key features and capabilities
- Project status/version

## Setup
### Development
- System requirements
- Installation from source
- Setting up development environment
- Dependencies: {', '.join(dependencies) if dependencies else 'None'}

### Production
- Package manager installation
- Container deployment (Docker)
- One-line install commands

## Configuration
- Environment variables: {', '.join([f'{k}=[VALUE]' for k in env_vars.keys()]) if env_vars else 'None'}
- Configuration files and their locations
- Security best practices

## Usage
- How to run the application
- Command line options/flags
- Examples of common use cases with code samples
- API documentation if applicable

## Deployment
- Containerization (Docker)
- Kubernetes manifests
- Cloud deployment (AWS/GCP/Azure)
- Scaling considerations

## Contributing
- How to submit issues
- Pull request workflow
- Coding standards
- Testing requirements

## Tests
- How to run the test suite
- Coverage reporting
- Writing new tests

## Support
- How to get help
- Community forums
- Commercial support options

## License
- License type (e.g., MIT, Apache)
- Copyright notice

## Acknowledgments
- Third-party libraries
- Inspiration/credits
- Team members

Project Description:
{project.description}

Technical Documentation:
{project.documentation}

Use proper Markdown formatting with:
- Clear section headers
- Consistent indentation
- Code blocks for commands
- Tables where appropriate
- Badges for build status/version (if available)
- Actual values from project context (no placeholders)"""

        llm_response_dict = await self.llm_client.call_llm(
            prompt=prompt, model_name=settings.ARCHITECT_MODEL
        )
        response_text = llm_response_dict.get("text_response", "")

        if response_text.startswith("Error:"):
            logger.error(f"Architect Agent: Error generating README: {response_text}")
            return f"# ERROR\n{response_text}"

        return response_text
