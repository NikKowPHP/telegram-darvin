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
        """Generate a comprehensive verification report with detailed analysis."""
        # ROO-AUDIT-TAG :: feature-006-automated-verification.md :: Create verification report
        report_prompt = f"""
        Create a detailed verification report with these sections:
        
        1. Summary:
           - Overall validity: {'Valid' if verification_results['valid'] else 'Invalid'}
           - Total issues found: {len(verification_results.get('issues', []))}
        
        2. Requirements Analysis:
           {self._format_requirements(verification_results.get('requirements', {}))}
        
        3. TODO Items Status:
           {self._format_todo_items(verification_results.get('todo_list', []))}
        
        4. Code Quality Assessment:
           - Architecture alignment
           - Consistency with codebase
           - Style and conventions
        
        5. Issues Found:
           {self._format_issues(verification_results.get('issues', []))}
        
        6. Recommendations:
           - Suggested improvements
           - Refactoring opportunities
           - Potential optimizations
        
        Use clear section headers and bullet points for readability.
        """
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
        
    def _format_requirements(self, requirements: Dict[str, Any]) -> str:
        """Format requirements for the report."""
        return '\n'.join([f"- {key}: {'Implemented' if value else 'Missing'}"
                        for key, value in requirements.items()])
    
    def _format_todo_items(self, todo_list: List[str]) -> str:
        """Format TODO items for the report."""
        return '\n'.join([f"- {item}" for item in todo_list])
    
    def _format_issues(self, issues: List[str]) -> str:
        """Format issues for the report."""
        return '\n'.join([f"- {issue}" for issue in issues]) or "No significant issues found"
    
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
        # ROO-AUDIT-TAG :: feature-007-readme-generation.md :: Implement project summary extraction
        project_summary = self.extract_project_summary(project_details)
        readme_template = self._get_readme_template()
        return self.llm_client.generate(
            f"Create a comprehensive README using this template:\n{readme_template}\n\nProject Summary:\n{project_summary}"
        )

    def extract_project_summary(self, project_details: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key project information for README generation."""
        # ROO-AUDIT-TAG :: feature-007-readme-generation.md :: Add setup and usage instructions
        prompt = f"""
        Analyze these project details and extract comprehensive information for a README file:
        
        Project Details:
        {project_details}
        
        Extract the following sections:
        1. Project Name and Description
        2. Main Features
        3. Technology Stack (including specific versions if available)
        4. Key Requirements
        5. Setup Instructions:
           - Installation steps
           - Configuration requirements
           - Environment setup
           - Dependencies installation
        6. Usage Examples:
           - Basic commands
           - Common use cases
           - API endpoints if applicable
        7. Development Guidelines:
           - Testing instructions
           - Contribution guidelines
        
        For setup instructions, generate specific commands based on the technology stack.
        For usage examples, provide concrete code snippets or command-line examples.
        
        Return the information in JSON format with those section names as keys.
        """
        return self.llm_client.generate_structured(prompt)

    def _get_readme_template(self) -> str:
        """Retrieve the README template."""
        from app.prompts.architect_readme_generation import README_TEMPLATE
        return README_TEMPLATE
    # ROO-AUDIT-TAG :: feature-007-readme-generation.md :: END

# ROO-AUDIT-TAG :: feature-006-automated-verification.md :: END