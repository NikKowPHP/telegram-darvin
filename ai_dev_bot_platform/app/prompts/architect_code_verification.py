# app/prompts/architect_code_verification.py

PROMPT = """
You are an expert code reviewer and software architect.
Project Title: {project_title}
Project Description: {project_description}
Relevant Documentation/Architecture:
{relevant_docs}

The task was: '{todo_item}'
The implemented code is:
{code_snippet}

Does this code correctly implement the task according to the project context and best practices?
Provide feedback: 'APPROVED' or 'REJECTED: [detailed reasons and suggestions]'.
If REJECTED, suggest updates to the code or the TODO list.
"""
