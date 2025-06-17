# Master Development Plan: Transition to Full Autonomy

**Project Goal:** Refactor the AI Development Bot from a user-driven, reactive service into a fully autonomous, proactive agent-based system as defined by the `.roo/` rules. The system will manage the entire project lifecycle in the background, driven by file-system state changes (signal files), not direct user commands.

---

- [ ] **Phase 1: Establish the Core Autonomous Loop & Project Manifest**
    - **Goal:** Replace the current reactive, Telegram-driven execution model with a persistent, proactive loop that runs the Roo `Orchestrator` agent. Implement the system's foundational state file, `project_manifest.json`.
    - **(Creates `work_items/item-001-core-loop.md`)**

- [ ] **Phase 2: Integrate TDD and Version Control into the Developer Agent**
    - **Goal:** Empower the `Developer` agent to execute its TDD cycle, commit code to version control, and signal completion as per its rules, bridging the gap between the current Python `ImplementerAgent` logic and the required autonomous behavior.
    - **(Creates `work_items/item-002-developer-integration.md`)**

- [ ] **Phase 3: Implement the Full Code Review and QA Cycle**
    - **Goal:** Activate the `TechLead` and `QAEngineer` agents by implementing their core review logic (static analysis, testing) and state-based signaling (`TECH_LEAD_APPROVED.md`, `NEEDS_REFACTOR.md`).
    - **(Creates `work_items/item-003-review-cycle.md`)**

- [ ] **Phase 4: Finalize Autonomy and Simplify the Telegram Interface**
    - **Goal:** Deprecate the complex logic in the current `ModelOrchestrator` and `handlers.py`. The Telegram bot will be simplified into a "dumb terminal" whose only job is to create new work items, thereby kicking off the autonomous factory.
    - **(Creates `work_items/item-004-interface-simplification.md`)**