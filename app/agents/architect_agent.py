from typing import Dict, List
from app.models.project import Project
from app.utils.llm_client import LLMClient
import logging

logger = logging.getLogger(__name__)

class ArchitectAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    async def generate_project_readme(self, project: Project, project_files_content: List[Dict[str,str]]) -> str:
        logger.info(f"Architect Agent: Generating README.md for project {project.id} - {project.title}")
        
        all_files_summary = "\n\n".join([f"File: {f['file_path']}\n```\n{f['content'][:500]}...\n```" for f in project_files_content])

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
        
        readme_content = await self.llm_client.call_gemini(prompt, model_name="gemini-1.5-pro-latest")
        
        if readme_content.startswith("Error:"):
            logger.error(f"Error generating README for project {project.id}: {readme_content}")
            return f"Error: Could not generate README.md. LLM Error: {readme_content}"
        return readme_content