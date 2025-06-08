Okay, this is a significant task, and breaking it down for a 4B model requires extreme granularity and clear, sequential steps. The "prod condition" implies not just code but also basic configuration, environment variable handling, logging stubs, and Dockerization.

This `implementation_todo.md` will be very long. It will assume the 4B LLM is guided by a human or a more capable LLM to execute these steps, especially for reviewing, testing, and integrating complex parts. The 4B model will primarily focus on generating code snippets and file structures based on very specific instructions.

**Assumptions for the 4B LLM:**
1.  It can create files and write Python code based on detailed prompts.
2.  It understands basic project structures (directories, `__init__.py`).
3.  It can fill in simple configurations and placeholders.
4.  It will require human review and integration for complex logic or inter-service communication.
5.  It will create stubs/placeholders where full logic is too complex for one go.

Let's begin.

---

# `implementation_todo.md` - AI-Powered Development Assistant Bot

**Project Goal:** Implement the AI-Powered Development Assistant Telegram Bot platform, ready for initial production deployment.
**Primary Technologies:** Python, FastAPI, SQLAlchemy, PostgreSQL, Redis, Celery, Docker, Kubernetes, `python-telegram-bot`, Google Gemini, OpenRouter.
**Source of Truth for Features & Architecture:** `documentation/high_level_documentation.md` and other supporting documents in `documentation/`.

---




## Phase RF0: Project Structure Rectification

**Goal:** Establish `ai_dev_bot_platform/` as the definitive project root and consolidate all application code and primary files within it.

*   `[ ]` **RF0.1: Consolidate `main.py`**
    *   Action:
        1.  Locate the `main.py` file currently at the repository root.
        2.  Move this `main.py` file into the `ai_dev_bot_platform/` directory.
        3.  If a `main.py` file already exists inside `ai_dev_bot_platform/` (e.g., from P0.4 of the original todo, which was specified to be `ai_dev_bot_platform/main.py`), ensure the content from the *repository root* `main.py` (which includes FastAPI setup and logging initialization) is the one that remains at `ai_dev_bot_platform/main.py`. Overwrite if necessary, preserving the correct functionality.
    *   Verification:
        1.  The file `ai_dev_bot_platform/main.py` exists.
        2.  The content of `ai_dev_bot_platform/main.py` includes `from fastapi import FastAPI`, `from app.core.logging_config import setup_logging`, `app = FastAPI(...)`, and `setup_logging()`.
        3.  The repository root directory no longer contains a `main.py` file.

*   `[ ]` **RF0.2: Consolidate `requirements.txt`**
    *   Action:
        1.  Locate the `requirements.txt` file currently at the repository root.
        2.  Move this `requirements.txt` file into the `ai_dev_bot_platform/` directory.
    *   Verification:
        1.  The file `ai_dev_bot_platform/requirements.txt` exists and contains the list of project dependencies.
        2.  The repository root directory no longer contains a `requirements.txt` file.

*   `[ ]` **RF0.3: Consolidate `.env.example`**
    *   Action:
        1.  Locate the `.env.example` file currently at the repository root.
        2.  Move this `.env.example` file into the `ai_dev_bot_platform/` directory.
    *   Verification:
        1.  The file `ai_dev_bot_platform/.env.example` exists and contains the example environment variables.
        2.  The repository root directory no longer contains an `.env.example` file.

*   `[x]` **RF0.4: Review and Remove Redundant Root `app/` Directory**
    *   Action:
  

**1. Files to be MOVED (as they are the primary/only correct versions or need to be placed in the new structure):**

*   **`app/agents/implementer_agent.py`**:
    *   **Reason:** This file only exists in the root `app/agents/` directory. It needs to be moved to `ai_dev_bot_platform/app/agents/implementer_agent.py`. Its internal imports (e.g., `from app.utils.llm_client import LLMClient`) will correctly resolve once it's in the target `ai_dev_bot_platform/app/` structure.
    *   **Action for Roo:** Move this file.

*   **`app/core/config.py`**:
    *   **Reason:** This file only exists in the root `app/core/` directory. It contains the correct `Settings` class as defined in P0.6 of `todos/implementation_todo.md`. It needs to be moved.
    *   **Action for Roo:**
        1.  Create the directory `ai_dev_bot_platform/app/core/`.
        2.  Create an empty `ai_dev_bot_platform/app/core/__init__.py` file.
        3.  Move `app/core/config.py` to `ai_dev_bot_platform/app/core/config.py`.

*   **`app/core/logging_config.py`**:
    *   **Reason:** This file only exists in the root `app/core/` directory. It contains the correct `setup_logging` function as defined in P0.7. It needs to be moved.
    *   **Action for Roo:** Move `app/core/logging_config.py` to `ai_dev_bot_platform/app/core/logging_config.py` (the `core` directory should now exist).

**2. Files Requiring a Small MERGE Action (then discard root version):**

*   **`app/agents/architect_agent.py`**:
    *   **Root Version (`app/agents/architect_agent.py`):** Contains the import `from typing import Dict, Any`.
    *   **Target Version (`ai_dev_bot_platform/app/agents/architect_agent.py`):** Does *not* contain this import but is otherwise the preferred version due to its placement.
    *   **Action for Roo:**
        1.  Open `ai_dev_bot_platform/app/agents/architect_agent.py`.
        2.  Add the line `from typing import Dict, Any` to its imports.
        3.  The root `app/agents/architect_agent.py` can then be ignored/deleted later.

**3. Files where the version in `ai_dev_bot_platform/app/` is SUPERIOR or IDENTICAL (and correctly placed), so the root `app/` version can be DISCARDED:**

*   **`app/models/project.py`**:
    *   **Reason:** The version in `ai_dev_bot_platform/app/models/project.py` is more complete (includes `tech_stack`, `current_todo_markdown`).
    *   **Action for Roo:** No merge needed. The root `app/models/project.py` can be ignored/deleted later.

*   **`app/schemas/project.py`**:
    *   **Reason:** The version in `ai_dev_bot_platform/app/schemas/project.py` is more complete.
    *   **Action for Roo:** No merge needed. The root `app/schemas/project.py` can be ignored/deleted later.

*   **`app/services/orchestrator_service.py`**:
    *   **Reason:** The version in `ai_dev_bot_platform/app/services/orchestrator_service.py` is significantly more advanced and implements much of the Phase 2 logic.
    *   **Action for Roo:** No merge needed. The root `app/services/orchestrator_service.py` can be ignored/deleted later.

*   **`app/services/project_service.py`**:
    *   **Reason:** The content is nearly identical. The version in `ai_dev_bot_platform/app/services/project_service.py` is preferred due to its correct placement for future import resolution.
    *   **Action for Roo:** No merge needed. The root `app/services/project_service.py` can be ignored/deleted later.

*   **`app/utils/llm_client.py`**:
    *   **Reason:** The content is essentially identical. The version in `ai_dev_bot_platform/app/utils/llm_client.py` is preferred due to its correct placement.
    *   **Action for Roo:** No merge needed. The root `app/utils/llm_client.py` can be ignored/deleted later.

**Summary of Actions for Roo for RF0.4:**

1.  **Create Directory and `__init__.py`:**
    *   Create `ai_dev_bot_platform/app/core/`.
    *   Create `ai_dev_bot_platform/app/core/__init__.py` (empty).

2.  **Move Files:**
    *   Move `app/agents/implementer_agent.py` to `ai_dev_bot_platform/app/agents/implementer_agent.py`.
    *   Move `app/core/config.py` to `ai_dev_bot_platform/app/core/config.py`.
    *   Move `app/core/logging_config.py` to `ai_dev_bot_platform/app/core/logging_config.py`.

3.  **Perform Merge Action:**
    *   Open `ai_dev_bot_platform/app/agents/architect_agent.py`.
    *   Add `from typing import Dict, Any` to its imports.

4.  **Final Cleanup (after the above actions and verification):**
    *   Delete the entire *repository root* `app/` directory.

This should consolidate everything correctly into `ai_dev_bot_platform/app/`. After these steps, proceed to task RF0.5 (Update Import Paths), though many imports should already be correct due to this careful consolidation.

*   `[x]` **RF0.5: Update Import Paths (System-Wide)**
    *   Action: Roo needs to simulate or be instructed that the **working directory for Python execution will now be `ai_dev_bot_platform/`**. This means all absolute imports within the `app` subdirectories should still start with `app.module...`.
        1.  Review all Python files within `ai_dev_bot_platform/app/` (e.g., `main.py` which is now `ai_dev_bot_platform/main.py`, all files in `services/`, `agents/`, `telegram_bot/`, `db/`, etc.).
        2.  Ensure all internal project imports are correct relative to the `ai_dev_bot_platform/` directory being the top-level for execution context.
            *   Example: In `ai_dev_bot_platform/main.py`, `from app.core.logging_config import setup_logging` should still be correct if `main.py` is run from within `ai_dev_bot_platform/`.
            *   Example: In `ai_dev_bot_platform/app/services/orchestrator_service.py`, imports like `from app.schemas.user import User` should remain correct.
        3.  Pay special attention to how `settings` from `app.core.config` is imported and used, and how database sessions are managed.
    *   Verification: Perform a conceptual check. If you were to run `python main.py` from within the `ai_dev_bot_platform` directory, or `python app/telegram_bot/bot_main.py` (also from `ai_dev_bot_platform`), imports should resolve correctly. (Actual execution test by human later).

---

## Phase RF1: Implement Critical Database Session Management

**Goal:** Implement the missing `app/db/session.py` and correctly integrate it.

*   `[x]` **RF1.1: Create `ai_dev_bot_platform/app/db/session.py`**
    *   Action: Create the file `ai_dev_bot_platform/app/db/session.py`.
    *   File Content (as per P0.8 of `implementation_todo.md`):
        ```python
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker, declarative_base
        from app.core.config import settings # Assuming config.py is correctly located at app/core/config.py

        SQLALCHEMY_DATABASE_URL = settings.get_database_url()

        engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base = declarative_base()

        # Dependency to get DB session (for FastAPI or general use)
        def get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
        ```
    *   Verification:
        1.  File `ai_dev_bot_platform/app/db/session.py` exists with the specified content.
        2.  The import `from app.core.config import settings` is correct based on the new structure.

*   `[x]` **RF1.2: Update `ai_dev_bot_platform/app/db/init_db.py`**
    *   Action: Modify `ai_dev_bot_platform/app/db/init_db.py`.
    *   Modify imports: Change `from app.db.session import engine, Base` (if it was already attempted) to correctly point to the newly created `session.py`. It should already be correct if it was `from app.db.session import ...`
    *   Ensure `Base.metadata.create_all(bind=engine)` uses `engine` and `Base` imported from `app.db.session`.
    *   Content should look like this (confirming imports from `app.models` for `User`, `Project`, `ProjectFile` are also correct relative to `ai_dev_bot_platform/app/`):
        ```python
        from app.db.session import engine, Base # Ensure this import is correct
        from app.models.user import User
        from app.models.project import Project
        from app.models.project_file import ProjectFile
        # Import other models as they are created

        def init_db():
            Base.metadata.create_all(bind=engine)
            print("Database tables initialized/checked.")

        if __name__ == "__main__":
            # Ensure imports for settings or other direct needs in __main__ are fine
            # if this script is run directly from ai_dev_bot_platform/
            # e.g. if init_db itself used settings directly, it would need:
            # from app.core.config import settings (but it doesn't directly)
            init_db()
        ```
    *   Verification: `init_db.py` imports `engine` and `Base` from `app.db.session`.

*   `[x]` **RF1.3: Update `ai_dev_bot_platform/app/telegram_bot/handlers.py`**
    *   Action: Modify `ai_dev_bot_platform/app/telegram_bot/handlers.py`.
    *   Ensure it imports `SessionLocal` from `app.db.session` (e.g., `from app.db.session import SessionLocal`).
    *   Ensure `db: Session = SessionLocal()` is used correctly within the handlers.
    *   Verification: `handlers.py` uses `SessionLocal` from the correct `app.db.session`.

*   `[ ]` **RF1.4: Update SQLAlchemy Model Files (`user.py`, `project.py`, `project_file.py`)**
    *   Action: For each model file in `ai_dev_bot_platform/app/models/`:
        1.  Ensure they import `Base` from `app.db.session` (e.g., `from app.db.session import Base`).
    *   Verification: All model files correctly import `Base`.

---

## Phase RF2: Create Missing Directories

**Goal:** Create the directory structure as initially specified.

*   `[ ]` **RF2.1: Create `ai_dev_bot_platform/app/background_tasks/` Directory**
    *   Action: Create the directory `background_tasks` inside `ai_dev_bot_platform/app/`.
    *   Action: Create an empty `__init__.py` file inside `ai_dev_bot_platform/app/background_tasks/`.
    *   Verification: Directory and `__init__.py` exist.

*   `[ ]` **RF2.2: Create `ai_dev_bot_platform/tests/` Directory**
    *   Action: Create the directory `tests` inside `ai_dev_bot_platform/`.
    *   Action: Create an empty `__init__.py` file inside `ai_dev_bot_platform/tests/` (optional for tests, but good practice).
    *   Verification: Directory exists.

*   `[ ]` **RF2.3: Create `ai_dev_bot_platform/scripts/` Directory**
    *   Action: Create the directory `scripts` inside `ai_dev_bot_platform/`.
    *   Verification: Directory exists.

---

## Phase RF3: Address Service Inconsistencies

**Goal:** Ensure service layers are implemented and used consistently.

*   `[ ]` **RF3.1: Refactor `ProjectService` to be Class-Based**
    *   Action: Modify `ai_dev_bot_platform/app/services/project_service.py`.
    *   Refactor the existing standalone functions (`create_project`, `get_project`, `get_projects_by_user`, `update_project`) into methods of a class named `ProjectService`.
    *   The class methods will take `self` and `db: Session` as primary arguments, followed by other necessary parameters.
    *   Example structure:
        ```python
        from sqlalchemy.orm import Session
        from app.models.project import Project
        from app.schemas.project import ProjectCreate, ProjectUpdate
        from typing import Optional, List
        import uuid

        class ProjectService:
            def create_project(self, db: Session, project_in: ProjectCreate, user_id: int) -> Project:
                # ... implementation ...
                db_project = Project(
                    user_id=user_id,
                    title=project_in.title,
                    # ... rest of fields
                )
                db.add(db_project)
                db.commit()
                db.refresh(db_project)
                return db_project

            def get_project(self, db: Session, project_id: uuid.UUID) -> Optional[Project]:
                # ... implementation ...
                return db.query(Project).filter(Project.id == project_id).first()
            
            # ... other methods ...
        ```
    *   Verification: `project_service.py` contains a `ProjectService` class with the specified methods.

*   `[ ]` **RF3.2: Update `ModelOrchestrator` to use Class-Based `ProjectService`**
    *   Action: Modify `ai_dev_bot_platform/app/services/orchestrator_service.py`.
    *   In `ModelOrchestrator.__init__`:
        *   Change `self.project_service = ProjectService()` to instantiate the class.
    *   In `ModelOrchestrator` methods (e.g., `_handle_new_project`):
        *   Ensure calls are made like `self.project_service.create_project(self.db, project_in=project_data, user_id=user.id)`.
    *   Verification: Orchestrator correctly instantiates and calls methods on `ProjectService` instance.

*   `[ ]` **RF3.3: Refactor `ProjectFileService` to be Class-Based (if not already)**
    *   Action: Review `ai_dev_bot_platform/app/services/project_file_service.py`.
    *   If it contains standalone functions, refactor them into methods of a class `ProjectFileService` similar to RF3.1.
    *   Standardize method names: e.g., ensure `create_project_file` is used if that's the intended name (orchestrator was calling `create_file`). Decide and make consistent. Recommendation: `create_project_file`.
    *   Verification: `project_file_service.py` uses a class structure if chosen, and method names are consistent with orchestrator calls.

*   `[ ]` **RF3.4: Update `ModelOrchestrator` for `ProjectFileService`**
    *   Action: Modify `ai_dev_bot_platform/app/services/orchestrator_service.py`.
    *   In `ModelOrchestrator.__init__`:
        *   Ensure `self.project_file_service = ProjectFileService()` (or similar) correctly instantiates it.
    *   In `_handle_implement_task`:
        *   Ensure calls to `project_file_service` use the correct method name (e.g., `self.project_file_service.create_project_file(self.db, ...)`).
    *   Verification: Orchestrator uses `ProjectFileService` correctly.

---

## Phase RF4: Update `implementation_todo.md`

**Goal:** Correct the status of P1.6.

*   `[ ]` **RF4.1: Mark P1.6 in `todos/implementation_todo.md` as Complete**
    *   Action:
        1.  Open the main `todos/implementation_todo.md` file.
        2.  Locate the line for task `P1.6: API Key Manager - Basic Structure`.
        3.  Change `[ ]` to `[x]` for this item.
        *   It should now read: `*   [x]` **P1.6: API Key Manager - Basic Structure**
    *   Verification: The checkbox for P1.6 in `todos/implementation_todo.md` is marked as `[x]`.

---

**Final Instruction for Roo:**
After completing all tasks in this `refactor_and_fix_todo.md` file, create a final Git commit summarizing these corrective actions. For example: `git commit -m "refactor(project): Rectify project structure and fix critical DB/service issues"`. Then, await further instructions or proceed to the next phase of the original `implementation_todo.md`.



**Note:** Phases 3-6 would follow a similar pattern of defining models, services, agent logic, and orchestrator updates. This initial set provides a very detailed start for the first major hurdles. Human oversight will be critical for guiding the 4B LLM, especially with complex parsing, state management in the orchestrator, and robust error handling.

This plan is already very long. Subsequent phases would cover:
*   **Phase 3: Codebase Indexing, Verification Loop & Basic Aider Integration:**
    *   Vector DB setup (e.g., FAISS locally or cloud service).
    *   Codebase Indexing Service (`app/services/codebase_indexing_service.py`).
    *   Orchestrator calls Architect for verification after Implementer.
    *   Implementer uses Aider (basic command execution via subprocess) for applying changes.
*   **Phase 4: Monetization & User Management Details:**
    *   `model_pricing`, `api_key_usage`, `credit_transactions` models and services.
    *   Accurate credit deduction in Orchestrator for Gemini & OpenRouter calls.
    *   `/credits` command, `/status` command enhancements.
*   **Phase 5: Polish, `README.md` Generation (for user projects) & Pre-Production Testing:**
    *   Architect Agent generates `README.md` for the *user's generated project*.
    *   Refine error handling, logging.
    *   More comprehensive manual testing of full flows.
*   **Phase 6: Dockerization, Basic K8s Manifests & Deployment Prep:**
    *   `Dockerfile` for the main application (FastAPI + Telegram Bot + Celery Worker in one image, or separate images).
    *   `docker-compose.yml` for local development.
    *   Basic Kubernetes `Deployment` and `Service` YAMLs for key components.
    *   Refine environment variable handling for K8s (ConfigMaps, Secrets).

This level of detail is necessary for a smaller LLM. Each `[ ]` is a promptable unit of work, with the surrounding context provided. Good luck!