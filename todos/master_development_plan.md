# Master Development Plan: Transition to Full Autonomy

**Project Goal:** Refactor the AI Development Bot from a user-driven assistant into a fully autonomous agent. The system will manage the entire project lifecycle (planning, implementation, self-healing, and delivery) in the background after receiving the initial user prompt, providing only high-level progress updates.

---

- [x] **Phase 1: Foundational Asynchronous Overhaul**
    - **Goal:** Decouple the user-facing Telegram bot from the long-running build process. The bot's role will be simplified to only kick-starting the autonomous workflow.
    - **(Creates `todos/dev_todo_phase_1_autonomy_foundations.md`)**

- [ ] **Phase 2: Refactoring the `ModelOrchestrator` for Autonomous Control**
    - **Goal:** Break down the existing monolithic `_handle_` methods into smaller, reusable, and state-agnostic functions. This prepares the class for the new autonomous loop without yet implementing the loop itself.
    - **(Creates `todos/dev_todo_phase_2_orchestrator_refactor.md`)**

- [ ] **Phase 3: Implementing the Autonomous Loop & Self-Healing Mechanism**
    - **Goal:** Implement the primary `while` loop within a new top-level function. This loop will orchestrate the task execution, verification, and the critical self-healing retry logic using feedback from the Architect. This is the new "brain" of the system.
    - **(Creates `todos/dev_todo_phase_3_autonomous_loop.md`)**

- [ ] **Phase 4: Finalization and Cleanup**
    - **Goal:** Remove all obsolete code, UI elements (like Telegram buttons), and update documentation to reflect the new, fully autonomous workflow. This ensures the system is clean and maintainable.
    - **(Creates `todos/dev_todo_phase_4_cleanup.md`)**