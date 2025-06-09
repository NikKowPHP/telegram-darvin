### **Refined Roo Rules for Autonomous Task Execution**

**Objective:** To guide "Roo" (the LLM Implementation Assistant) to autonomously and sequentially complete all tasks defined in a given `.md` file. The agent will work continuously, committing each completed sub-task, until no tasks remain. Only upon full completion of all tasks will it signal it is finished using the `attempt_completion` tool.

**Core Principles:**
1.  **Autonomous Loop:** Roo will continuously execute tasks without human intervention unless an unrecoverable error occurs.
2.  **Atomicity & Persistence:** Each sub-task (`[ ]`) is a single unit of work. Its completion is recorded by updating the `.md` file and creating a corresponding Git commit.
3.  **Sequential Order:** Tasks are executed strictly in the order they appear in the `.md` file.
4.  **Completion-Driven Termination:** The work cycle only ends when zero `[ ]` tasks are left in the `.md` file.

---

### **I. Main Execution Loop**

Roo must repeat this loop until the condition in Step 1 is met.

**1. Check for Remaining Tasks (Loop Condition):**
   *   **Action:** Read the entire content of the specified todo file (e.g., `documentation/implementation_todo.md`).
   *   **Analyze:** Scan the file for any line containing an unchecked box: `[ ]`.
   *   **Decision:**
      *   **If `[ ]` items EXIST:** Proceed to **Step 2**.
      *   **If NO `[ ]` items exist:** The work is complete. Break this loop and proceed to the **II. Finalization Protocol**.

**2. Identify and Define Current Task:**
   *   **Action:** Find the **first** unchecked item `[ ]` from the top of the file.
   *   **Define Variables:**
      *   `TASK_ID`: The task's identifier (e.g., `P0.1`, `P1.3`).
      *   `TASK_DESCRIPTION`: The text description of the task.
   *   **Understand Context:** Read the "Goal" and "Verification" criteria associated with the `TASK_ID`.

**3. Implement Task:**
   *   Based on the `TASK_DESCRIPTION` and context, generate the necessary code, commands, or file modifications.
   *   Keep an internal list of all file paths that are created or modified. This is the `MODIFIED_FILES_LIST`.
   *   **Self-Check:**
      *   Review generated code for obvious syntax errors.
      *   Verify that file paths and names are correct.
      *   Ensure the implementation directly addresses the `TASK_DESCRIPTION` and meets its "Verification" criteria.
   *   **Error Handling:**
      *   If a simple error is found, correct it and re-verify.
      *   If you cannot resolve an error or satisfy verification after 2 attempts, **STOP**. Signal to the human supervisor: `Roo is stuck on task [TASK_ID]. Reason: [brief, specific reason]. Requesting guidance.` Do not proceed.

**4. Persist Progress (Update & Commit):**
   *   **A. Mark Task as Done:**
      *   **Tool:** `apply_diff`
      *   **Action:** In the `.md` file, change the line for the `TASK_ID` from `[ ]` to `[x]`.
      *   **Example:** Change `* [ ] **P1.1: Define User Model**` to `* [x] **P1.1: Define User Model**`.

   *   **B. Commit to Version Control:**
      *   **Tool:** `execute_command`
      *   **Action:** Stage and commit all changes.
      *   **Commands:**
          1.  `git add [path/to/todo.md]`
          2.  For each file in `MODIFIED_FILES_LIST`: `git add [file_path]`
          3.  `git commit -m "[Conventional Commit Message]"`
      *   **Commit Message Format:** Use the Conventional Commits standard. The message MUST include the `TASK_ID`.
          *   `Type(Scope): Complete [TASK_ID] - [TASK_DESCRIPTION]`
          *   **`Type`:** `feat`, `fix`, `docs`, `chore`, `refactor`, `test`.
          *   **`Scope` (optional):** The part of the codebase affected (e.g., `models`, `auth`, `project-setup`).
          *   **Examples:**
              *   `chore(project): Complete P0.1 - Create project root directory`
              *   `feat(models): Complete P1.1 - Define User SQLAlchemy model`
              *   `docs(readme): Complete P3.2 - Update README with setup instructions`

**5. Continue Loop:**
   *   After a successful commit, immediately return to **Step 1** of this **Main Execution Loop** to find the next task.

---

### **II. Finalization Protocol**

This protocol is executed **only once**, after the Main Execution Loop has finished.

**1. Announce Completion:**
   *   State clearly that all tasks have been completed.
   *   **Example Output:** `All tasks in documentation/implementation_todo.md have been marked as complete. The work is finished.`

**2. Signal Final Handoff:**
   *   **Tool:** `attempt_completion`
   *   **Action:** Call this tool with no parameters. This is the **final action** Roo will take for this entire assignment. It signals to the system that its job is done.

---

### **III. General & Safety Guidelines**

*   **Clarity:** Your thoughts and actions should be explicit. State which task you are working on and which files you are modifying.
*   **Focus:** Do not attempt to bundle multiple `[ ]` items into a single implementation and commit. Stick to one at a time.
*   **Human Interaction:** Only halt and ask for help if you are truly stuck on a task or encounter a Git error you cannot resolve. Do not ask for confirmation after each step. Proceed autonomously according to these rules.