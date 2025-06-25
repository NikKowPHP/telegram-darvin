# ROO-AUDIT-TAG :: feature-006-automated-verification.md :: Extend Architect agent for verification
from typing import Dict, Any
from app.utils.llm_client import LLMClient
from app.services.codebase_indexing_service import CodebaseIndexingService

class ArchitectAgent:
    """Agent responsible for architectural planning and verification."""
    
    def __init__(self, llm_client: LLMClient, index_service: CodebaseIndexingService):
        self.llm_client = llm_client
        self.index_service = index_service
        
    def verify_implementation(self, code: str, requirements: Dict[str, Any], todo_list: List[str],
                            task_description: str, master_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Verify code implementation for autonomous loop with extended checks."""
        # ROO-AUDIT-TAG :: feature-009-autonomous-loop.md :: Extend verification for autonomous workflow
        # Get more context with higher similarity threshold
        context = self.index_service.search_codebase(code, k=10, threshold=0.7)
        # Filter and format relevant context
        filtered_context = [
            f"File: {item['file']}\nContent:\n{item['content']}\n"
            for item in context
            if item['score'] > 0.5
        ]
        verification_prompt = self._build_verification_prompt(
            code, requirements, todo_list, filtered_context, task_description, master_plan)
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
        
    def _build_verification_prompt(self, code: str, requirements: Dict[str, Any], todo_list: List[str],
                                 context: List[str], task_description: str, master_plan: Dict[str, Any]) -> str:
        """Build enhanced verification prompt for autonomous loop."""
        context_str = '\n'.join(context) or "No relevant context found"
        return f"""
        Analyze this code implementation for the autonomous development loop:
        
        Implementation Code:
        {code}
        
        Project Requirements:
        {requirements}
        
        Pending TODO Items:
        {todo_list}
        
        Relevant Codebase Context:
        {context_str}
        
        Verification Checklist for Autonomous Development:
        1. Does the code directly address the specific task? ({task_description})
        2. Does it fulfill all specified requirements?
        3. Are all relevant TODO items addressed?
        4. Does it align with the master plan? ({master_plan.get('summary', '')})
        5. Does it integrate well with existing patterns?
        6. Are there any inconsistencies with the codebase?
        7. Does it follow project conventions and style?
        8. Does it move the project closer to completion?
        
        Provide detailed feedback on any issues found, specifically assessing:
        - How well the code addresses the specific task
        - Progress made toward project completion
        - Any architectural drift introduced
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

    def assess_progress(self, completed_tasks: List[Dict[str, Any]], total_tasks: int) -> Dict[str, Any]:
        """Assess project progress based on completed tasks."""
        # ROO-AUDIT-TAG :: feature-009-autonomous-loop.md :: Implement progress assessment
        progress_percent = (len(completed_tasks) / total_tasks) * 100
        return {
            'completed': len(completed_tasks),
            'total': total_tasks,
            'progress': f"{progress_percent:.1f}%",
            'on_track': progress_percent >= (completed_tasks[-1]['timestamp'] - completed_tasks[0]['timestamp']).days
        }
# ROO-AUDIT-TAG :: feature-009-autonomous-loop.md :: END