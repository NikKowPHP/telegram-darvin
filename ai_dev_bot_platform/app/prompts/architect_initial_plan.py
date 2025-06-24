# app/prompts/architect_initial_plan.py

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

**CRITICAL:** Ensure the Technology Stack is a valid JSON object inside a code block as specified. Do not add any text before or after the JSON block for that section.
"""
