

### **Ticket: `TASK-AUT-001` - Implement Fully Autonomous Development Loop**

**Project:** AI Dev Bot Platform
**Epic:** Core Automation Engine
**Priority:** Highest

---

#### **1. Title**

Implement a fully autonomous development loop triggered by a single user command after the initial plan is generated.

#### **2. User Story**

As a user, after I have provided my project requirements and the system has generated an initial plan, I want to be able to click a single "Start Implementation" button. This action should trigger a fully autonomous process where the AI agents work together to complete all the tasks in the generated TODO list without any further intervention from me, so that I can receive a fully coded project at the end.

#### **3. Acceptance Criteria (AC)**

1.  **Trigger:** The autonomous process must be initiated *only* when the user clicks the `▶️ Start Autonomous Implementation` button (with `callback_data` format `implement:start:{project_id}`).
2.  **State Machine:** The system must be able to read the `current_todo_markdown` from the `Project` model in the database.
3.  **Task Iteration:** The system must autonomously iterate through each task in the markdown list that is marked with `- [ ]`.
4.  **Implementation:** For each task, the `OrchestratorService` must call the `ImplementerAgent` to generate or modify the necessary code and file paths.
5.  **Verification:** After the `ImplementerAgent` completes a task, the `OrchestratorService` must call the `ArchitectAgent` to verify the generated code against the task requirements.
6.  **State Update (Success):** If the Architect `APPROVES` the code, the system must:
    *   Persist the new/modified file(s) to storage (`StorageService`).
    *   Update the `current_todo_markdown` in the database, changing the task's status from `- [ ]` to `- [x]`.
    *   Send a brief, non-blocking status update to the user's Telegram chat (e.g., "✅ Task 'Set up database schema' completed.").
    *   Automatically proceed to the next task marked with `- [ ]`.
7.  **State Update (Failure):** If the Architect `REJECTS` the code, the autonomous loop must:
    *   Log the failure and the rejection reason.
    *   Send a notification to the user that the process has been paused due to a verification failure, including the reason.
    *   Stop the loop and await further instruction (manual intervention, out of scope for this ticket).
8.  **Completion:** When all tasks in the list are marked as `- [x]`, the system must send a final "Implementation Complete" message to the user.
9.  **Asynchronous Execution:** The entire autonomous loop must run as a background task (e.g., using `asyncio.create_task`) so it does not block the main application or the Telegram bot.

#### **4. Technical Implementation Plan**

This feature will be primarily implemented within the `OrchestratorService`, with a new entry point in the `button_handler`.

1.  **`OrchestratorService`: New Method `execute_autonomous_loop`**
    *   Create a new public method: `async def execute_autonomous_loop(self, project_id: uuid.UUID, telegram_chat_id: int):`.
    *   This method will act as the "engine" for the autonomous process.
    *   **Loop Logic:**
        *   Fetch the project from the database using `project_id`.
        *   Use a helper function to parse `current_todo_markdown` and find the *first* task string that starts with `- [ ]`.
        *   If no such task is found, the process is complete. Notify the user and `return`.
        *   Notify the user: "🚀 Starting task: '{task_description}'..."
        *   Call `ImplementerAgent` to implement the task. The agent will need the project context, tech stack, and the specific task description. It should also have access to the current project file structure from storage.
        *   The `ImplementerAgent` returns a dictionary of `{'file_path': 'code_content'}`.
        *   Call `ArchitectAgent.verify_implementation_step()` with the new code.
        *   Based on the `APPROVED`/`REJECTED` status, update the project's TODO markdown and save the files, as described in the ACs.
        *   After a successful step, recursively call `self.execute_autonomous_loop(project_id, telegram_chat_id)` or use a `while` loop to continue to the next task.

2.  **`Telegram Bot`: Update `button_handler`**
    *   In `app/telegram_bot/handlers.py`, add a new `if` condition to the `button_handler` to catch the `implement:start:{project_id}` callback.
    *   When this callback is received:
        *   Extract the `project_id`.
        *   Send a confirmation message to the user: "🚀 Autonomous implementation initiated! I will send you updates as tasks are completed."
        *   Instantiate the `OrchestratorService`.
        *   Call `asyncio.create_task(orchestrator.execute_autonomous_loop(project_id, chat_id))` to kick off the background process.

3.  **Helper Function: Task Parsing**
    *   A private helper method within `OrchestratorService` will be needed, e.g., `_get_next_task(markdown_text)`. This function will parse the markdown string and return the description of the first open task, or `None` if all are complete.
    *   A second helper, `_update_task_status(markdown_text, task_description)`, will take the markdown and a completed task, and return a new markdown string with that task marked as `[x]`.

#### **5. Files to be Modified**

*   **`app/services/orchestrator_service.py`**: Add the new `execute_autonomous_loop` method and its private helpers.
*   **`app/telegram_bot/handlers.py`**: Modify `button_handler` to handle the new callback and trigger the orchestrator.
*   **`app/agents/implementer_agent.py`**: Ensure the `implement_todo_item` method can effectively use the file context provided by the orchestrator to modify existing files or create new ones.
*   **`app/services/project_service.py`**: No changes likely needed, but will be used to update the project's markdown.

#### **6. Future Enhancements (Out of Scope for this Ticket)**

*   Implement a retry mechanism for rejected tasks.
*   Allow the `ImplementerAgent` to use the `ArchitectAgent`'s rejection feedback to self-correct its code.
*   Provide a `/pause` or `/stop` command for the user to halt the autonomous process.