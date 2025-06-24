# Epic 1: Resolve the "Two Brains" Architectural Conflict

- [ ] (REFACTOR) Modify Telegram Bot handler to decouple from Python orchestration: `ai_dev_bot_platform/app/telegram_bot/handlers.py`
- [ ] (REFACTOR) Refactor ModelOrchestrator to ProjectHelpers library: `ai_dev_bot_platform/app/services/orchestrator_service.py`
- [ ] (NEW) Create CLI runner for Roo Agent integration: `ai_dev_bot_platform/cli_runner.py`
- [ ] (UPDATE) Update Roo rules to use new CLI: `.roo/rules-planner.md`, `.roo/rules-developer.md`