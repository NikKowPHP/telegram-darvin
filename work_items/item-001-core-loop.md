---
status: "open"
priority: "critical"
---

# Feature Request: Establish the Core Autonomous Loop and Project Manifest

## Description
The current system is triggered reactively by user messages on Telegram. To achieve autonomy, we must create a persistent, primary execution loop that continuously runs the `Orchestrator` agent. This agent, as defined in `.roo/rules-orchestrator/rules.md`, will then become the master router for the entire system.

This task also involves implementing the logic for creating the foundational `project_manifest.json` file, which is the "source of truth" for all other agents.

## Acceptance Criteria
1.  A new top-level Python script, `run_autonomy.py`, must be created.
2.  This script must contain a primary, infinite `while True:` loop.
3.  Inside the loop, the script must execute the Roo `Orchestrator` agent using a shell command (e.g., `subprocess.run(['roo', '-m', 'orchestrator'])`).
4.  The `Architect` agent's "Blueprint Mode" logic (from its rules) must be implemented. When the `Orchestrator` hands off to the `Architect` and no `project_manifest.json` exists, the `Architect` must:
    a. Check for `app_description.md` to infer project details.
    b. Create the `project_manifest.json` file in the workspace root with the correct structure as specified in `.roo/rules-architect/rules.md`.
    c. Create the `logs/system_events.log` file.
5.  A pause (e.g., `time.sleep(10)`) should be included in the `run_autonomy.py` loop to prevent rapid-fire execution and high CPU usage.