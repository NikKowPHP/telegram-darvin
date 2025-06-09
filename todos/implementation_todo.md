Of course. I will create a new, highly detailed `implementation_todo.md` file based on the analysis and recommended next steps.

This plan is meticulously structured for an autonomous 4B LLM agent. Each step is an atomic, explicit, and verifiable action, minimizing ambiguity and cognitive load. The goal is to guide the agent to elevate the application from its current state to a feature-complete and production-hardened system.

---
Here is the content for the new file:

# `implementation_todo.md` - From MVP to Production Readiness

**Project Goal:** To implement the remaining core features and production-hardening measures, making the AI Development Assistant robust, secure, and ready for deployment.

**Guiding Principle:** Complete each task sequentially. Do not move to the next `[ ]` item until the current one is finished and verified.

---

## Feature 1: Complete User-Facing Features (Credits & Delivery)

**Goal:** Implement the user-facing stubs for purchasing credits and the backend logic for delivering the final project as a ZIP file.

*   `[x]` **F1.1: Add "Buy Credits" buttons to the `/credits` command**
    *   **File:** `ai_dev_bot_platform/app/telegram_bot/handlers.py`
    *   **Action:**
        1.  At the top of the file, add the import: `from telegram import InlineKeyboardButton, InlineKeyboardMarkup`.
        2.  Find the `credits_command` function.
        3.  Replace the `await update.message.reply_text(...)` call with the following code to add buttons:
            ```python
            keyboard = [
                [InlineKeyboardButton("Buy 100 Credits ($10)", callback_data='buy_100')],
                [InlineKeyboardButton("Buy 500 Credits ($45)", callback_data='buy_500')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"Your current credit balance is: {user_db.credit_balance:.2f}.\n\n"
                "Purchase options will be available soon! Select an option to be notified:",
                reply_markup=reply_markup
            )
            ```
    *   **Verification:** The `/credits` command now displays two inline buttons for purchasing credits.

*   `[x]` **F1.2: Create a handler for the new "Buy Credits" buttons**
    *   **File:** `ai_dev_bot_platform/app/telegram_bot/handlers.py`
    *   **Action:**
        1.  Add a new function to the end of the file called `button_handler`:
            ```python
            async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
                query = update.callback_query
                await query.answer() # Acknowledge the button press
                
                # For now, this is a stub.
                await query.edit_message_text(
                    text=f"Thank you for your interest in purchasing credits. "
                         f"The payment system is not yet implemented. You selected: {query.data}"
                )
            ```
    *   **Verification:** A new `button_handler` function exists in `handlers.py`.

*   `[x]` **F1.3: Register the new button handler in the bot**
    *   **File:** `ai_dev_bot_platform/app/telegram_bot/bot_main.py`
    *   **Action:**
        1.  Add the import: `from telegram.ext import CallbackQueryHandler`.
        2.  In the `run_bot` function, add this line after the other `add_handler` calls:
            ```python
            application.add_handler(CallbackQueryHandler(button_handler))
            ```
        3.  Make sure `button_handler` is imported from `.handlers`.
    *   **Verification:** The `bot_main.py` now registers a `CallbackQueryHandler`. Clicking the "Buy Credits" buttons in Telegram now provides a response.

*   `[x]` **F1.4: Create a utility function to ZIP project files**
    *   **File:** `ai_dev_bot_platform/app/utils/file_utils.py` (Create this new file)
    *   **Action:** Add the following content to the new file. This function will create a ZIP archive in memory.
        ```python
        import io
        import zipfile
        from typing import List, Dict

        def create_project_zip(project_files: List[Dict[str, str]]) -> io.BytesIO:
            """
            Creates a ZIP file in memory from a list of project files.
            
            Args:
                project_files: A list of dictionaries, where each dict has "file_path" and "content".
                
            Returns:
                An in-memory bytes buffer containing the ZIP file.
            """
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for p_file in project_files:
                    # Ensure file_path is relative and safe
                    file_path = p_file.get("file_path", "unknown_file.txt")
                    content = p_file.get("content", "")
                    zip_file.writestr(file_path, content.encode('utf-8'))
            
            zip_buffer.seek(0)
            return zip_buffer
        ```
    *   **Verification:** The new file `app/utils/file_utils.py` exists and contains the `create_project_zip` function.

*   `[x]` **F1.5: Integrate ZIP creation and delivery into the Orchestrator**
    *   **File:** `ai_dev_bot_platform/app/services/orchestrator_service.py`
    *   **Action:**
        1.  At the top, add the import: `from app.utils.file_utils import create_project_zip`.
        2.  Modify the `process_user_request` method. Change its return type from `str` to a dictionary. The return dictionary will have the format `{'text': '...', 'zip_buffer': None}`.
        3.  Find the `_handle_implement_task` method.
        4.  Locate the section where the project status is set to `"completed"`.
        5.  Inside that block, after fetching the project files (`project_files_for_readme`), add this logic to create the ZIP file:
            ```python
            # Create ZIP file of the project
            zip_buffer = create_project_zip(project_files_for_readme)
            ```
        6.  Modify the final `return` statement in that block to return the dictionary with the zip buffer:
            ```python
            return {
                "text": (
                    f"Project '{project.title}' is complete! All tasks implemented and verified.\n"
                    f"README.md has been generated. Find your project attached."
                ),
                "zip_buffer": zip_buffer,
                "project_title": project.title
            }
            ```
        7.  Update all other `return` statements in the `ModelOrchestrator` to return the dictionary format, e.g., `return {'text': 'Some message', 'zip_buffer': None}`.
    *   **Verification:** The orchestrator now creates a ZIP file upon project completion and returns it in a dictionary structure.

*   `[x]` **F1.6: Update Telegram handler to send the ZIP file**
    *   **File:** `ai_dev_bot_platform/app/telegram_bot/handlers.py`
    *   **Action:**
        1.  Find the `message_handler` function.
        2.  Locate the line `response_text = await orchestrator.process_user_request(...)` and change it to `response_data = await orchestrator.process_user_request(...)`.
        3.  Replace `await update.message.reply_text(response_text)` with the following logic:
            ```python
            response_text = response_data.get('text')
            zip_buffer = response_data.get('zip_buffer')
            
            if response_text:
                await update.message.reply_text(response_text)

            if zip_buffer:
                project_title = response_data.get('project_title', 'project')
                file_name = f"{project_title.replace(' ', '_')}.zip"
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=zip_buffer,
                    filename=file_name
                )
            ```
    *   **Verification:** When a project is completed, the bot now sends the generated text message AND attaches the project ZIP file.

---

## Feature 2: Production Hardening: Database Migrations (Alembic)

**Goal:** Integrate Alembic to manage database schema changes safely, replacing the non-production `create_all()` method.

*   `[x]` **F2.1: Add Alembic to requirements**
    *   **File:** `ai_dev_bot_platform/requirements.txt`
    *   **Action:** Add the line `alembic` to the file.
    *   **Verification:** `requirements.txt` contains `alembic`.

*   `[x]` **F2.2: Create the `alembic.ini` configuration file**
    *   **File:** `ai_dev_bot_platform/alembic.ini` (Create this file in the project root)
    *   **Action:** Add the following content:
        ```ini
        [alembic]
        script_location = app/db/migrations
        sqlalchemy.url = postgresql://user:password@host:port/dbname

        [loggers]
        keys = root,sqlalchemy,alembic

        [handlers]
        keys = console

        [formatters]
        keys = generic

        [logger_root]
        level = WARN
        handlers = console
        qualname =

        [logger_sqlalchemy]
        level = WARN
        handlers =
        qualname = sqlalchemy.engine

        [logger_alembic]
        level = INFO
        handlers =
        qualname = alembic

        [handler_console]
        class = StreamHandler
        args = (sys.stderr,)
        level = NOTSET
        formatter = generic

        [formatter_generic]
        format = %(levelname)-5.5s [%(name)s] %(message)s
        datefmt = %H:%M:%S
        ```
    *   **Verification:** `alembic.ini` exists in the project root.

*   `[ ]` **F2.3: Create the Alembic `env.py` script**
    *   **File:** `ai_dev_bot_platform/app/db/migrations/env.py` (Create the `migrations` directory first)
    *   **Action:** Add the following content. This script tells Alembic how to find your models.
        ```python
        from logging.config import fileConfig
        from sqlalchemy import engine_from_config
        from sqlalchemy import pool
        from alembic import context

        # this is the Alembic Config object, which provides
        # access to the values within the .ini file in use.
        config = context.config

        # Interpret the config file for Python logging.
        # This line sets up loggers basically.
        if config.config_file_name is not None:
            fileConfig(config.config_file_name)

        # add your model's MetaData object here
        # for 'autogenerate' support
        from app.db.session import Base
        from app.models.user import User
        from app.models.project import Project
        from app.models.project_file import ProjectFile
        from app.models.api_key_models import ModelPricing, APIKeyUsage
        from app.models.transaction import CreditTransaction
        
        target_metadata = Base.metadata

        # other values from the config, defined by the needs of env.py,
        # can be acquired:
        # my_important_option = config.get_main_option("my_important_option")
        # ... etc.

        def run_migrations_offline() -> None:
            """Run migrations in 'offline' mode.
            This configures the context with just a URL
            and not an Engine, though an Engine is acceptable
            here as well.  By skipping the Engine creation
            we don't even need a DBAPI to be available.
            Calls to context.execute() here emit the given string to the
            script output.
            """
            url = config.get_main_option("sqlalchemy.url")
            context.configure(
                url=url,
                target_metadata=target_metadata,
                literal_binds=True,
                dialect_opts={"paramstyle": "named"},
            )

            with context.begin_transaction():
                context.run_migrations()


        def run_migrations_online() -> None:
            """Run migrations in 'online' mode.
            In this scenario we need to create an Engine
            and associate a connection with the context.
            """
            from app.core.config import settings
            alembic_config = config.get_section(config.config_ini_section)
            alembic_config['sqlalchemy.url'] = settings.get_database_url()
            connectable = engine_from_config(
                alembic_config,
                prefix="sqlalchemy.",
                poolclass=pool.NullPool,
            )

            with connectable.connect() as connection:
                context.configure(
                    connection=connection, target_metadata=target_metadata
                )

                with context.begin_transaction():
                    context.run_migrations()


        if context.is_offline_mode():
            run_migrations_offline()
        else:
            run_migrations_online()
        ```
    *   **Verification:** The `app/db/migrations/env.py` file exists and is populated.

*   `[ ]` **F2.4: Remove old database initialization logic**
    *   **File:** `ai_dev_bot_platform/app/db/init_db.py`
    *   **Action:** Delete this file. It is no longer needed and should not be used.
    *   **Verification:** The file `app/db/init_db.py` has been deleted.

---

## Feature 3: Production Hardening: Observability & Testing

**Goal:** Add a health check endpoint for Kubernetes and create the first unit test for the application.

*   `[ ]` **F3.1: Add a health check endpoint to the API**
    *   **File:** `ai_dev_bot_platform/main.py`
    *   **Action:** In the `app = FastAPI(...)` section, find the `@app.get("/")` endpoint. Directly below it, add a new endpoint for health checks:
        ```python
        @app.get("/health")
        async def health_check():
            return {"status": "ok"}
        ```
    *   **Verification:** When the app is running, navigating to `/health` returns `{"status": "ok"}`.

*   `[ ]` **F3.2: Update Kubernetes manifest with health probes**
    *   **File:** `deploy/kubernetes/app-k8s.yaml`
    *   **Action:** Find the `containers:` section for the `ai-dev-bot-app`. Add `livenessProbe` and `readinessProbe` to it.
        ```yaml
        # ... inside spec.template.spec.containers array
        - name: ai-dev-bot-app
          image: your-repo/ai-dev-bot-app:latest
          ports:
          - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 20
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 45
            periodSeconds: 30
          envFrom:
        #... rest of file
        ```
    *   **Verification:** The `app-k8s.yaml` deployment now includes probe configurations.

*   `[ ]` **F3.3: Add testing libraries to requirements**
    *   **File:** `ai_dev_bot_platform/requirements.txt`
    *   **Action:** Add the following lines to the file:
        ```
        pytest
        pytest-mock
        ```
    *   **Verification:** `requirements.txt` contains `pytest` and `pytest-mock`.

*   `[ ]` **F3.4: Create the first unit test**
    *   **File:** `ai_dev_bot_platform/tests/test_services.py` (Create this new file and the `tests` directory if it doesn't exist)
    *   **Action:** Add the following content to create a test for the `UserService`.
        ```python
        import pytest
        from unittest.mock import MagicMock
        from app.services.user_service import UserService
        from app.models.user import User
        from decimal import Decimal

        def test_get_user_by_telegram_id():
            # 1. Setup
            mock_db_session = MagicMock()
            user_service = UserService()
            
            test_user_id = 12345
            expected_user = User(
                id=1, 
                telegram_user_id=test_user_id, 
                username="testuser", 
                credit_balance=Decimal("10.00")
            )

            # 2. Mock the DB call
            mock_db_session.query.return_value.filter.return_value.first.return_value = expected_user
            
            # 3. Action
            result_user = user_service.get_user_by_telegram_id(mock_db_session, telegram_user_id=test_user_id)
            
            # 4. Assert
            assert result_user is not None
            assert result_user.telegram_user_id == test_user_id
            assert result_user.username == "testuser"
            mock_db_session.query.return_value.filter.return_value.first.assert_called_once()
        ```
    *   **Verification:** The `tests/test_services.py` file exists and contains a valid `pytest` test. A human supervisor can run `pytest` from the root directory to confirm it passes.