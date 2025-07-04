# app/prompts/architect_initial_plan.py

# ROO-AUDIT-TAG :: feature-003-architectural-planning.md :: Documentation templates
PROMPT = """
You are a senior software architect. Your task is to analyze the following project requirements and create a structured development plan.

**Project Title:** '{project_title}'

**Project Requirements:**
---
{project_requirements}
---

**Instructions:**

1.  **Technical Overview:** Write a brief, one-paragraph technical overview of the proposed solution.
2.  **Technology Stack:** Analyze the user's requirements for any mentioned technologies. If none are mentioned, suggest a modern, appropriate stack. Structure your response ONLY as a valid JSON object within a markdown code block. The JSON object must have keys: "frontend", "backend", "database", and "infrastructure". If the user provided a stack, use it.
    ```json
    {{
      "frontend": ["React", "Next.js", "Tailwind CSS"],
      "backend": ["Node.js", "Express"],
      "database": ["PostgreSQL", "Prisma"],
      "infrastructure": ["Docker", "Vercel"]
    }}
    ```
3.  **Implementation TODO List:** Generate a detailed, step-by-step TODO list in Markdown task list format (e.g., `- [ ] Task description`). The tasks should be logical and actionable for a developer to follow. Start this section with the exact heading: `### Implementation TODO List`.

4.  **Documentation Templates:**
    Generate templates for key documentation sections using the following structure:
    
    ### Architecture Overview
    [Describe the high-level system architecture here]
    
    ### API Specifications
    ```markdown
    ## Endpoints
    - `GET /api/resource`: Description
    - `POST /api/resource`: Description
    ```
    
    ### Data Models
    ```json
    {{
      "ModelName": {{
        "field1": "type|description",
        "field2": "type|description"
      }}
    }}
    ```
    
    ### Deployment Instructions
    ```markdown
    ## Prerequisites
    - Requirement 1
    - Requirement 2
    
    ## Deployment Steps
    1. Step 1
    2. Step 2
    ```
    
    ### Testing Strategy
    ```markdown
    ## Test Types
    - Unit Tests: [Description]
    - Integration Tests: [Description]
    
    ## Test Execution
    ```bash
    pytest tests/ --cov=app
    ```
    ```

**CRITICAL:** Ensure the Technology Stack is a valid JSON object inside a code block as specified. Do not add any text before or after the JSON block for that section.
"""
# ROO-AUDIT-TAG :: feature-003-architectural-planning.md :: END
