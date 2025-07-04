# Canonical Specification: AI-Powered Development Assistant Bot

## 1. Project Overview

This Telegram bot serves as an autonomous software development assistant that takes user requirements and delivers complete, production-ready applications. The bot leverages a sophisticated **Model Orchestrator** that intelligently routes tasks to either a **large "Architect" Language Model (LLM)** for planning, documentation, and verification, or **smaller "Implementer" LLMs** for code execution, utilizing models accessed directly from **Google Gemini** and a diverse range via **OpenRouter**. A key component enhancing this process is **codebase indexing**, which provides deep contextual understanding of the generated code for more accurate implementation and verification. Upon project completion, a detailed `README.md` with setup and usage instructions is automatically generated. The system incorporates a **credit-based monetization model**, providing initial free credits and requiring users to purchase additional credits for continued use, all managed through a diligent cost-tracking mechanism.

## 2. Core Functional Requirements

- **Requirement Gathering:** The system will gather detailed requirements through conversational interfaces.
- **Hierarchical AI Collaboration:** A Model Orchestrator will route tasks to specialized Architect or Implementer agents.
- **Architectural Planning:** An Architect LLM will generate comprehensive technical documentation, select optimal technology stacks, and create detailed, actionable TODO markdown lists.
- **Codebase Indexing:** A service will maintain an up-to-date, searchable representation of the project's code to provide context for all AI operations.
- **Iterative Implementation:** Implementer LLMs will systematically execute tasks from the TODO list, marking items as complete and committing code.
- **Automated Verification:** The Architect LLM will meticulously review the work done by Implementer LLMs, cross-referencing the TODO list, project requirements, and the codebase index.
- **README Generation:** Upon project completion, the Architect LLM will generate a comprehensive `README.md` file detailing setup, configuration, and execution steps.
- **Credit-Based Monetization:** User access is managed through a credit system, with costs tracked and deducted for all LLM API usage.

## 3. System Architecture

The system is composed of several key services: a Telegram Bot Interface, a Model Orchestrator, Architect and Implementer Agents, a Codebase Indexing Service, and a Cost Management & Billing System.

- **Technology Stack:**
  - **Backend:** Python 3.11+, FastAPI, SQLAlchemy, Alembic
  - **AI Integration:** Google Gemini (direct), OpenRouter (aggregator)
  - **Infrastructure:** PostgreSQL, Redis, Celery, Docker, Kubernetes

## 4. API Endpoints

### Autonomous Development Loop Trigger
- **Endpoint**: `POST /orchestrate/run-loop`
- **Authentication**: Required (JWT token)
- **Parameters**:
  ```json
  {
    "project_id": "UUID of the project to run loop for"
  }
  ```
- **Success Response**:
  ```json
  {
    "status": "success",
    "project_id": "UUID of the project",
    "result": {
      "task": "Description of executed task",
      "message": "Task execution status"
    }
  }
  ```
- **Error Responses**:
  - `400 Bad Request`: Missing or invalid project_id
  - `500 Internal Server Error`: Failed to run autonomous loop
- **Example**:
  ```bash
  curl -X POST http://api.example.com/orchestrate/run-loop \
    -H "Authorization: Bearer {token}" \
    -H "Content-Type: application/json" \
    -d '{"project_id": "123e4567-e89b-12d3-a456-426614174000"}'
  ```

## 5. Database Schema

The system will use the following PostgreSQL schema:

-   **users**: Manages user data and platform credit balance.
-   **projects**: Tracks the state and metadata of each development project.
-   **api_keys**: Securely stores API keys for LLM providers.
-   **model_pricing**: Maintains up-to-date pricing for various LLM models to calculate costs.
-   **api_key_usage**: Logs every call to an LLM API for cost tracking and auditing.
-   **credit_transactions**: Records all changes to a user's credit balance.
-   **conversations**: Stores the history of interactions for a project.
-   **project_files**: Contains the content of all files generated for a project.