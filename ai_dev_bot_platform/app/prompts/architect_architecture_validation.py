# app/prompts/architect_architecture_validation.py

PROMPT = """
As an expert architect, validate this project's technical design:
        
Project: {project_title}
Description: {project_description}
Current Tech Stack: {tech_stack}

Identify any:
1. Architectural anti-patterns
2. Technology mismatches
3. Scaling limitations
4. Security concerns
5. Deployment challenges

Provide specific recommendations for improvement.
"""
