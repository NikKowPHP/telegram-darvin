---
status: "open"
priority: "high"
---

# Feature Request: Implement the Full Code Review and QA Cycle

## Description
With the `Developer` agent now able to commit code, we need to activate the quality-control agents: `TechLead` and `QAEngineer`. These agents are triggered by signal files (`commit_complete.md`, `tech_lead_approved.md`) and must perform their respective checks.

## Acceptance Criteria
1.  The `TechLead` agent, when triggered by `commit_complete.md`, must delete the signal file.
2.  The `TechLead` must execute `git diff HEAD~1 HEAD` to review the latest changes.
3.  The `TechLead` must run static analysis and unit tests using the command specified in its rules (`cd [project_root] && npm test`).
4.  Based on the review, the `TechLead` must create either `tech_lead_approved.md` on success or `NEEDS_REFACTOR.md` (with specific feedback) on failure.
5.  The `QAEngineer` agent, when triggered by `tech_lead_approved.md`, must delete the signal file.
6.  The `QAEngineer` must run acceptance tests (`cd [project_root] && npm run test:e2e`).
7.  Based on test results, the `QAEngineer` must create either `qa_approved.md` on success or `NEEDS_REFACTOR.md` on failure.