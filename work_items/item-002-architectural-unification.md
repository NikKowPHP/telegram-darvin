# Project Plan: Unification & Completion

## Objective

To refactor the AI Development Platform to resolve all identified architectural conflicts, implement the specified persistent services, complete the user-facing credit purchase flow, and establish a single, clear execution model. Upon completion of this plan, the system will be functionally complete as per the `canonical_spec.md`.

## Guiding Principles

*   Sequential Execution: Each epic and task must be completed in the order presented. Do not proceed to the next task until the current one is fully implemented and verified.
*   Atomic Commits: Each task should result in a single, logical commit.
*   Documentation First: The `README.md` and other documentation will be the final step, updated to reflect the new, unified architecture.

---

## Epic 1: Resolve the "Two Brains" Architectural Conflict

**Goal:** Designate the Roo Agent `Dispatcher` as the single, authoritative orchestrator and refactor the Python `ModelOrchestrator` into a stateless service library.

*   **Task 1.1: Decouple the Telegram Bot from Python Orchestration**
    *   **File:** `ai_dev_bot_platform/app/telegram_bot/handlers.py`
    *   **Action:** Modify the `message_handler`. Remove the call to `orchestrator.process_user_request`.
    *   **New Logic:** When a new project description is received, the `message_handler` should now perform only these actions:
        1.  Create a unique project directory (e.g., using UUID).
        2.  Write the user's message content into a new `app_description.md` file within that directory.
        3.  The Roo `Dispatcher`'s existing rules will automatically detect this new project and hand off to the `product-manager` agent, correctly starting the autonomous loop.
    *   **Verification:** Sending a project description to the bot no longer runs the Python orchestrator but successfully creates the project directory and `app_description.md` file.

*   **Task 1.2: Refactor `ModelOrchestrator` to `ProjectHelpers` Library**
    *   **File:** `ai_dev_bot_platform/app/services/orchestrator_service.py`
    *   **Action:**
        1.  Rename the file to `ai_dev_bot_platform/app/services/project_helpers.py`.
        2.  Rename the class `ModelOrchestrator` to `ProjectHelpers`.
        3.  **Delete** the primary control method `process_user_request`.
        4.  Refactor methods like `_handle_new_project`, `_handle_implement_task`, and `_deduct_credits_for_llm_call` to be stateless helper functions. They should accept all required data (like `user`, `project_id`, etc.) as direct arguments.
    *   **Verification:** The `ModelOrchestrator` class no longer exists. The new `ProjectHelpers` class contains stateless functions.

*   **Task 1.3: Create a CLI for Roo Agent Integration**
    *   **File:** `ai_dev_bot_platform/cli_runner.py` (Create new file).
    *   **Action:** Create a simple command-line interface using `argparse` or `click`. This script will be the bridge that allows Roo agents (which can run shell commands) to use the Python helper functions.
    *   **Example Commands to Implement:**
        *   `python cli_runner.py generate-plan --project-id <id> --description "..."` (Calls the relevant method from `ProjectHelpers`).
        *   `python cli_runner.py implement-task --project-id <id> --task "..."`
        *   `python cli_runner.py deduct-credits --user-id <id> --input-tokens 100 --output-tokens 200 ...`
    *   **Verification:** The CLI script can be executed from the command line and successfully calls the functions in `project_helpers.py`.

*   **Task 1.4: Update Roo Rules to Use the CLI**
    *   **Files:** `.roo/rules-planner.md`, `.roo/rules-developer.md`, etc.
    *   **Action:** Modify the rules for agents that need to perform complex actions. Instead of having complex internal logic, they will now execute the `cli_runner.py` script with the appropriate arguments.
    *   **Example (in `developer/rules.md`):** `Execute: python cli_runner.py implement-task --project-id ...`
    *   **Verification:** The Roo agents' execution logs show successful calls to the new CLI script.

---

## Epic 2: Implement Persistent Codebase Indexing

**Goal:** Replace the temporary, in-memory `faiss-cpu` indexer with a persistent `pgvector` solution and a Celery-based background processing system, as already planned.

*   **Task 2.1: Execute Existing Refactor Plan**
    *   **File:** `documentation/scaling_on_raspberry.md`
    *   **Action:** Implement the **entire** step-by-step `implementation_todo.md` found within this file. This includes:
        1.  Setting up Celery for background tasks.
        2.  Creating the Telegram notification utility.
        3.  Refactoring the `message_handler` to dispatch jobs to Celery.
        4.  Updating dependencies to use `pgvector` and remove `faiss-cpu`.
        5.  Creating the `ProjectEmbedding` model.
        6.  Refactoring the `CodebaseIndexingService` to use `pgvector` and a separate embedding service.
    *   **Verification:** All tasks from the pre-existing plan are marked as complete.

*   **Task 2.2: Generate and Apply `pgvector` Database Migration**
    *   **Action:** After creating the `ProjectEmbedding` model (as part of Task 2.1), run the following command: `alembic revision --autogenerate -m "Add project_embeddings table for pgvector"`.
    *   **Action:** Review the generated migration file to ensure it correctly creates the table with a `Vector` column type.
    *   **Action:** Apply the migration: `alembic upgrade head`.
    *   **Verification:** The `project_embeddings` table exists in the PostgreSQL database.

---

## Epic 3: Complete the Credit Purchase Web Flow

**Goal:** Create the minimal web UI necessary to handle Stripe payment redirects, completing the monetization loop.

*   **Task 3.1: Create Payment Status Endpoints**
    *   **File:** `ai_dev_bot_platform/main.py`
    *   **Action:** Add two new `GET` endpoints that return simple HTML responses.
        *   `@app.get("/payment-success", response_class=HTMLResponse)`
        *   `@app.get("/payment-cancelled", response_class=HTMLResponse)`
    *   **Verification:** Navigating to these endpoints in a browser shows the corresponding success/cancellation message.

*   **Task 3.2: Implement HTML Responses**
    *   **File:** `ai_dev_bot_platform/main.py`
    *   **Action:** Inside the new endpoints, return simple, self-contained HTML strings. The HTML should inform the user of the status and instruct them to return to their Telegram chat.
    *   **Verification:** The HTML content is styled minimally and provides clear instructions.

*   **Task 3.3: Update `PaymentService` to Use New Endpoints**
    *   **File:** `ai_dev_bot_platform/app/services/payment_service.py`
    *   **Action:** Modify the `create_checkout_session` method. Change the `success_url` and `cancel_url` parameters to use the new endpoints (e.g., `success_url=f"{settings.WEBAPP_URL}/payment-success"`).
    *   **Verification:** Initiating a credit purchase from the bot now redirects to a Stripe page that, upon completion, sends the user to the correct new success/cancel page.

---

## Epic 4: Unify Documentation and Entry Points

**Goal:** Make the project's execution model unambiguous and update all documentation to reflect the new, unified architecture.

*   **Task 4.1: Update `docker-compose.yml` Entry Point**
    *   **File:** `ai_dev_bot_platform/docker-compose.yml`
    *   **Action:** Change the `command` for the `app` service. Instead of `uvicorn main:app ...`, it should now be `python run_autonomy.py`. The FastAPI/Uvicorn server for the webhook will need to be run by this script or a supervisor process within the container. A simple approach is to have `run_autonomy.py` start uvicorn as a background process.
    *   **Verification:** Running `docker-compose up` now starts the autonomous Roo `Dispatcher` loop directly.

*   **Task 4.2: Rewrite `README.md` Execution Instructions**
    *   **File:** `README.md`
    *   **Action:** Completely rewrite the "Running Locally" and "Deployment" sections to reflect the new, single entry-point model.
    *   **New Instructions:** The guide should clearly state:
        1.  Set up the `.env` file.
        2.  Run `docker-compose up -d postgres redis`.
        3.  Run `alembic upgrade head`.
        4.  Run `python run_autonomy.py` to start the entire system's logic loop.
        5.  Explain that the Stripe webhook is the only part that requires separate exposure (e.g., with `ngrok`).
    *   **Verification:** A new developer can successfully set up and run the entire project using only the revised `README.md` instructions.