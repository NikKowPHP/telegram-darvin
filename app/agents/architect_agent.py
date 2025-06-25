# ROO-AUDIT-TAG :: feature-006-automated-verification.md :: Extend Architect agent for verification
from typing import Dict, Any
from app.utils.llm_client import LLMClient
from app.services.codebase_indexing_service import CodebaseIndexingService

class ArchitectAgent:
    """Agent responsible for architectural planning and verification."""
    
    def __init__(self, llm_client: LLMClient, index_service: CodebaseIndexingService):
        self.llm_client = llm_client
        self.index_service = index_service
        
    def verify_implementation(self, code: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Verify code implementation against project requirements."""
        # ROO-AUDIT-TAG :: feature-006-automated-verification.md :: Implement code verification
        context = self.index_service.search_codebase(code)
        verification_prompt = self._build_verification_prompt(code, requirements, context)
        verification_result = self.llm_client.generate(verification_prompt)
        
        return {
            'valid': 'valid' in verification_result.lower(),
            'issues': self._parse_verification_issues(verification_result),
            'context': context
        }
        
    def generate_verification_report(self, verification_results: Dict[str, Any]) -> str:
        """Generate a detailed verification report."""
        # ROO-AUDIT-TAG :: feature-006-automated-verification.md :: Create verification report
        report_prompt = self._build_report_prompt(verification_results)
        return self.llm_client.generate(report_prompt)
        
    def _build_verification_prompt(self, code: str, requirements: Dict[str, Any], context: List[Dict]) -> str:
        """Build verification prompt for LLM."""
        return f"""
        Verify if this code meets the project requirements:
        Code:
        {code}
        
        Requirements:
        {requirements}
        
        Codebase Context:
        {context}
        """
        
    def _parse_verification_issues(self, verification_result: str) -> List[str]:
        """Parse verification issues from LLM response."""
        # Placeholder implementation
        return []

    # ROO-AUDIT-TAG :: feature-007-readme-generation.md :: Extend Architect agent for README generation
    def generate_readme(self, project_details: Dict[str, Any]) -> str:
        """Generate a README file based on project details."""
        readme_template = self._get_readme_template()
        return self.llm_client.generate(
            f"Create a comprehensive README using this template:\n{readme_template}\n\nProject Details:\n{project_details}"
        )

    def _get_readme_template(self) -> str:
        """Retrieve the README template."""
        # This will be implemented after creating the template file
        return "# {Project Name}\n\n## Description\n\n{Project Description}"
    # ROO-AUDIT-TAG :: feature-007-readme-generation.md :: END

# ROO-AUDIT-TAG :: feature-006-automated-verification.md :: END