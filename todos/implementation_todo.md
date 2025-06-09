Of course. Based on the detailed verification report, I will now create a new `implementation_todo.md` file.

This file is designed with a small 4B LLM in mind. The steps are extremely granular, sequential, and explicit to minimize ambiguity and ensure the model can complete the tasks successfully.

---
Here is the content for the new file:

# `implementation_todo.md` - Critical Fixes for Production Readiness

**Project Goal:** To resolve critical bugs, operational gaps, and architectural inconsistencies identified in the verification report. Completing these tasks will make the application stable, functional, and ready for deployment.

**Guiding Principle:** Each task is an atomic unit of work. Complete one task, verify it, and then move to the next.

---

## Fix 1: Repair Credit Deduction System (Critical)

**Goal:** Ensure that LLM token usage data is correctly passed from the Agents to the Orchestrator so that credit deduction can function as designed.

*   `[x]` **F1.1: Update `ImplementerAgent` to handle LLM response dictionary**
    *   **File:** `ai_dev_bot_platform/app/agents/implementer_agent.py`
    *   **Action:**
        1.  Find the `implement_todo_item` method.
        2.  Locate the line: `code_response = await self.llm_client.call_openrouter(...)`
        3.  Rename the variable `code_response` to `llm_response_dict`. The line should now be: `llm_response_dict = await self.llm_client.call_openrouter(...)`
        4.  Directly below that line, add a new line to extract the text content: `code_response = llm_response_dict.get("text_response", "")`
        5.  Find the final `return` statement in the method. It currently looks like `return {"filename": filename, "code": code_content.strip()}`.
        6.  Modify it to include the full LLM response dictionary. The new return statement should be:
            ```python
            return {"filename": filename, "code": code_content.strip(), "llm_call_details": llm_response_dict}
            ```
    *   **Verification:** The `implement_todo_item` method now returns a dictionary that includes the `llm_call_details` key.

*   `[x]` **F1.2: Update `ArchitectAgent` (Planning) to return LLM details**
    *   **File:** `ai_dev_bot_platform/app/agents/architect_agent.py`
    *   **Action:**
        1.  Find the `generate_initial_plan_and_docs` method.
        2.  Locate the line: `response_text = await self.llm_client.call_gemini(...)`
        3.  Rename the variable `response_text` to `llm_response_dict`.
        4.  Directly below it, add a new line: `response_text = llm_response_dict.get("text_response", "")`
        5.  Find the final `return` statement in the `try` block. Modify it to include the LLM details:
            ```python
            return {
                "documentation": doc_content,
                "tech_stack_suggestion": tech_stack_str,
                "todo_list_markdown": todo_list_md,
                "llm_call_details": llm_response_dict
            }
            ```
    *   **Verification:** The `generate_initial_plan_and_docs` method now returns a dictionary containing the `llm_call_details` key.

*   `[x]` **F1.3: Update `ArchitectAgent` (Verification) to return LLM details**
    *   **File:** `ai_dev_bot_platform/app/agents/architect_agent.py`
    *   **Action:**
        1.  Find the `verify_implementation_step` method.
        2.  Locate the line: `response_text = await self.llm_client.call_gemini(...)`
        3.  Rename the variable `response_text` to `llm_response_dict`.
        4.  Directly below it, add a new line: `response_text = llm_response_dict.get("text_response", "")`
        5.  Find the `return` statements within this method. Modify all of them to include the `llm_call_details` key.
            *   Change `return {"status": "ERROR", "feedback": response_text}` to `return {"status": "ERROR", "feedback": response_text, "llm_call_details": llm_response_dict}`.
            *   Change `return {"status": "APPROVED", "feedback": response_text}` to `return {"status": "APPROVED", "feedback": response_text, "llm_call_details": llm_response_dict}`.
            *   Change `return {"status": "REJECTED", "feedback": response_text}` to `return {"status": "REJECTED", "feedback": response_text, "llm_call_details": llm_response_dict}`.
    *   **Verification:** The `verify_implementation_step` method now always returns a dictionary containing the `llm_call_details` key.

*   `[x]` **F1.4: Update Orchestrator to use new LLM details for credit deduction**
    *   **File:** `ai_dev_bot_platform/app/services/orchestrator_service.py`
    *   **Action:**
        1.  Find the `_handle_new_project` method. Locate the line `if "error" in plan_result:`. The credit deduction logic is right below it.
        2.  Ensure the call to `_deduct_credits_for_llm_call` uses `plan_result["llm_call_details"]`. The code should look like this:
            ```python
            # Deduct credits for LLM call if successful
            if "llm_call_details" in plan_result:
                await self._deduct_credits_for_llm_call(
                    user=user,
                    llm_response_data=plan_result["llm_call_details"],
                    task_type="planning",
                    project_id=project.id
                )
            ```
        3.  Find the `_handle_implement_task` method.
        4.  After the `implementation = await self.implementer_agent.implement_todo_item(...)` call, add the credit deduction logic for the **implementation** step:
            ```python
            # Deduct credits for implementation LLM call
            if "llm_call_details" in implementation:
                await self._deduct_credits_for_llm_call(
                    user=user,
                    llm_response_data=implementation["llm_call_details"],
                    task_type="implementation",
                    project_id=project.id
                )
            ```
        5.  In the same method, after the `verification_result = await self.architect_agent.verify_implementation_step(...)` call, add the credit deduction logic for the **verification** step:
            ```python
            # Deduct credits for verification LLM call
            if "llm_call_details" in verification_result:
                await self._deduct_credits_for_llm_call(
                    user=user,
                    llm_response_data=verification_result["llm_call_details"],
                    task_type="verification",
                    project_id=project.id
                )
            ```
    *   **Verification:** The orchestrator now calls `_deduct_credits_for_llm_call` after each of the three agent calls (planning, implementation, verification), using the correct nested dictionary.

---

## Fix 2: Integrate Telegram Bot into Application Startup

**Goal:** Ensure the Telegram bot polling process runs automatically when the application is started with Docker or Uvicorn.

*   `[x]` **F2.1: Make the bot's run function asynchronous**
    *   **File:** `ai_dev_bot_platform/app/telegram_bot/bot_main.py`
    *   **Action:**
        1.  Change the function definition `def run_bot():` to `async def run_bot():`.
        2.  Change the final line `application.run_polling()` to `await application.run_polling()`.
        3.  Remove the entire `if __name__ == "__main__":` block from the bottom of the file. It will no longer be run directly.
    *   **Verification:** The file `bot_main.py` now contains an `async def run_bot()` function and has no `if __name__ == "__main__":` block.

*   `[x]` **F2.2: Update main.py to manage the bot's lifecycle**
    *   **File:** `ai_dev_bot_platform/main.py`
    *   **Action:** Replace the entire content of the file with the following code. This adds the FastAPI `lifespan` manager to start the bot.
        ```python
        import asyncio
        from contextlib import asynccontextmanager
        from fastapi import FastAPI
        from app.core.logging_config import setup_logging
        from app.telegram_bot.bot_main import run_bot

        # Setup logging at the application's entry point
        setup_logging()

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # This code runs on startup
            print("Application startup: Starting Telegram bot in background...")
            loop = asyncio.get_event_loop()
            bot_task = loop.create_task(run_bot())
            yield
            # This code runs on shutdown
            print("Application shutdown: Stopping Telegram bot...")
            bot_task.cancel()
            try:
                await bot_task
            except asyncio.CancelledError:
                print("Bot task successfully cancelled.")

        app = FastAPI(title="AI Development Assistant API", lifespan=lifespan)

        @app.get("/")
        async def root():
            return {"message": "AI Development Assistant API is running and bot is active!"}
        ```
    *   **Verification:** `main.py` has been updated with the new content. When running `uvicorn main:app --reload`, the console should show "Starting Telegram bot in background..." and the bot should be responsive in Telegram.

---

## Fix 3: Standardize Service Layer and User Service

**Goal:** Refactor the function-based `user_service.py` into a class-based service to match the architecture of other services.

*   `[x]` **F3.1: Convert user_service.py to a class**
    *   **File:** `ai_dev_bot_platform/app/services/user_service.py`
    *   **Action:** Replace the entire content of the file with the following class-based implementation.
        ```python
        from sqlalchemy.orm import Session
        from app.models.user import User
        from app.schemas.user import UserCreate, UserUpdate
        from typing import Optional, List
        from decimal import Decimal

        class UserService:
            def get_user_by_telegram_id(self, db: Session, telegram_user_id: int) -> Optional[User]:
                return db.query(User).filter(User.telegram_user_id == telegram_user_id).first()

            def create_user(self, db: Session, user_in: UserCreate, initial_credits: Decimal = Decimal("10.00")) -> User:
                db_user = User(
                    telegram_user_id=user_in.telegram_user_id,
                    username=user_in.username,
                    email=user_in.email,
                    credit_balance=initial_credits
                )
                db.add(db_user)
                db.commit()
                db.refresh(db_user)
                return db_user

            def update_user_credits(self, db: Session, telegram_user_id: int, amount: Decimal, is_deduction: bool = True) -> Optional[User]:
                db_user = self.get_user_by_telegram_id(db, telegram_user_id)
                if db_user:
                    if is_deduction:
                        if db_user.credit_balance < amount:
                            return None # Insufficient credits
                        db_user.credit_balance -= amount
                    else:
                        db_user.credit_balance += amount
                    db.commit()
                    db.refresh(db_user)
                return db_user
        ```
    *   **Verification:** `user_service.py` now contains the `UserService` class with all the user-related methods inside it.

*   `[x]` **F3.2: Update Telegram handlers to use the new UserService class**
    *   **File:** `ai_dev_bot_platform/app/telegram_bot/handlers.py`
    *   **Action:**
        1.  Change the import from `from app.services import user_service` to `from app.services.user_service import UserService`.
        2.  In every handler function (`start_command`, `credits_command`, `message_handler`), find where `user_service` is used.
        3.  Before it's used, add this line to create an instance: `user_service = UserService()`.
        4.  Update all calls from `user_service.get_user_by_telegram_id(...)` to `user_service.get_user_by_telegram_id(...)` (no change here, but good to verify).
        5.  Update `user_service.create_user(...)` to `user_service.create_user(...)`.
    *   **Verification:** The handlers now import `UserService`, create an instance of it, and call its methods.

*   `[x]` **F3.3: Update Orchestrator to use the new UserService class**
    *   **File:** `ai_dev_bot_platform/app/services/orchestrator_service.py`
    *   **Action:**
        1.  At the top, change the import `from app.services.user_service import update_user_credits` to `from app.services.user_service import UserService`.
        2.  Inside the `ModelOrchestrator`'s `__init__` method, add a new line to initialize the service: `self.user_service = UserService()`.
        3.  Find the `_deduct_credits_for_llm_call` method.
        4.  Locate the line `updated_user = update_user_credits(...)`.
        5.  Change this call to use the instance: `updated_user = self.user_service.update_user_credits(...)`.
    *   **Verification:** The orchestrator now correctly initializes and uses the `UserService` class.

---

## Fix 4: Centralize Model Name Configuration

**Goal:** Remove hardcoded LLM model names from the agent code and manage them in the central configuration file.

*   `[x]` **F4.1: Add model names to the settings file**
    *   **File:** `ai_dev_bot_platform/app/core/config.py`
    *   **Action:** Inside the `Settings` class, add the following fields for model configuration:
        ```python
        # Model Configuration
        ARCHITECT_MODEL: str = "gemini-1.5-pro-latest"
        IMPLEMENTER_MODEL: str = "openrouter/auto" # Let OpenRouter decide the best model
        VERIFICATION_MODEL: str = "gemini-1.5-pro-latest"
        DEFAULT_GEMINI_MODEL: str = "gemini-1.5-flash-latest"
        ```
    *   **Verification:** The `Settings` class in `config.py` now contains these new configuration variables.

*   `[ ]` **F4.2: Update Agents and LLMClient to use settings**
    *   **File:** `ai_dev_bot_platform/app/agents/architect_agent.py`
    *   **Action:**
        1.  Add the import: `from app.core.config import settings`.
        2.  In `generate_initial_plan_and_docs`, find `model_name="gemini-1.5-pro-latest"` and change it to `model_name=settings.ARCHITECT_MODEL`.
        3.  In `verify_implementation_step`, find `model_name="gemini-1.5-pro-latest"` and change it to `model_name=settings.VERIFICATION_MODEL`.
    *   **File:** `ai_dev_bot_platform/app/agents/implementer_agent.py`
    *   **Action:**
        1.  Add the import: `from app.core.config import settings`.
        2.  In `implement_todo_item`, find the line `model_name = "openrouter/auto"`.
        3.  Change it to `model_name = settings.IMPLEMENTER_MODEL`.
    *   **File:** `ai_dev_bot_platform/app/utils/llm_client.py`
    *   **Action:**
        1.  Add the import: `from app.core.config import settings`.
        2.  In `call_gemini`, change the method signature from `async def call_gemini(self, prompt: str, model_name: str = "gemini-1.5-flash-latest")` to `async def call_gemini(self, prompt: str, model_name: str = None)`.
        3.  Inside `call_gemini`, add a check at the top: `if model_name is None: model_name = settings.DEFAULT_GEMINI_MODEL`.
    *   **Verification:** All hardcoded model names in the agents and the LLM client's default have been replaced with references to the `settings` object.