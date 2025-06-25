# ROO-AUDIT-TAG :: feature-006-automated-verification.md :: Extend Architect agent for verification
from typing import Dict, Any
from app.utils.llm_client import LLMClient
from app.services.codebase_indexing_service import CodebaseIndexingService

class ArchitectAgent:
    """Agent responsible for architectural planning and verification."""
    
    def __init__(self, llm_client: LLMClient, index_service: CodebaseIndexingService):
        self.llm_client = llm_client
        self.index_service = index_service
        
    def verify_implementation(self, code: str, requirements: Dict[str, Any], todo_list: List[str]) -> Dict[str, Any]:
        """Verify code implementation against project requirements and TODO list with codebase context."""
        # ROO-AUDIT-TAG :: feature-006-automated-verification.md :: Add codebase index integration
        # Get more context with higher similarity threshold
        context = self.index_service.search_codebase(code, k=10, threshold=0.7)
        # Filter and format relevant context
        filtered_context = [
            f"File: {item['file']}\nContent:\n{item['content']}\n"
            for item in context
            if item['score'] > 0.5
        ]
        verification_prompt = self._build_verification_prompt(code, requirements, todo_list, filtered_context)
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
        
    def _build_verification_prompt(self, code: str, requirements: Dict[str, Any], todo_list: List[str], context: List[str]) -> str:
        """Build context-aware verification prompt for LLM."""
        context_str = '\n'.join(context) or "No relevant context found"
        return f"""
        Analyze this code implementation considering the project context:
        
        Implementation Code:
        {code}
        
        Project Requirements:
        {requirements}
        
        Pending TODO Items:
        {todo_list}
        
        Relevant Codebase Context:
        {context_str}
        
        Verification Checklist:
        1. Does the code fulfill all specified requirements?
        2. Are all relevant TODO items addressed?
        3. Does the code integrate well with existing patterns?
        4. Are there any inconsistencies with the codebase?
        5. Does it follow project conventions and style?
        
        Provide detailed feedback on any issues found.
        """
        
    def _parse_verification_issues(self, verification_result: str) -> List[str]:
        """Parse verification issues from LLM response."""
        # ROO-AUDIT-TAG :: feature-006-automated-verification.md :: Parse verification issues
        issues = []
        lines = verification_result.split('\n')
        for line in lines:
            if line.strip().startswith('- '):
                issues.append(line.strip()[2:])
        return issues

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