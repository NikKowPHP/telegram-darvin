---
status: "open"
priority: "high"
---

# Feature Request: Integrate TDD and Version Control into the Roo Developer Agent

## Description
The current `ImplementerAgent` in Python can generate file content. However, the `Developer` Roo agent has a much more sophisticated set of responsibilities as per `.roo/rules-developer/rules.md`, including a Test-Driven Development (TDD) cycle, using `git` for version control, and signaling completion. This ticket bridges that gap.

## Acceptance Criteria
1.  The `Developer` agent must be able to execute the tactical plan from `active_plan_file` or `NEEDS_REFACTOR.md`.
2.  For each step, it must use the `project_root` from the manifest and execute shell commands with the `cd [project_root] && ...` prefix.
3.  It must follow the TDD loop:
    a. Write a failing test (`npm test` should fail).
    b. Write code to make the test pass (`npm test` should pass).
    c. Refactor the code.
4.  After completing an objective, the agent must commit all changes to the current branch using a standard `git commit` command.
5.  Upon successful commit, the agent must create the `commit_complete.md` signal file (path from the manifest) to hand off control to the `TechLead`.
6.  The agent must be able to handle failures by creating the `NEEDS_ASSISTANCE.md` signal file.