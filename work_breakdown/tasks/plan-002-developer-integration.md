# Phase 2: Integrate TDD and Version Control into the Developer Agent

- [x] (LOGIC) Update Developer agent to implement TDD cycle:
    - Read `project_manifest.json` to get paths
    - Close all open editor tabs at start
    - Prioritize `NEEDS_REFACTOR.md` if exists, else read active plan
    - Break down task into `current_task.md`
    - Implement code changes per `current_task.md`
    - Mark task complete in active plan
    - Commit changes and create `COMMIT_COMPLETE.md`

- [x] (LOGIC) Implement version control commands:
    - Add `git` commands for staging and committing
    - Commit message: "feat: Complete task: [Task Description]"

- [x] (LOGIC) Refactor existing ImplementerAgent code:
    - Replace relevant parts with new TDD cycle logic
    - Remove obsolete functionality

- [x] (LOGIC) Update Orchestrator to handle Developer handoff:
    - Add logic to trigger Tech Lead after commit complete