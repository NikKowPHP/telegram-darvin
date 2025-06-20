# Resolve Architectural Conflict

## Tasks

### (LOGIC) Decouple Telegram Bot from Python Orchestration
1. [ ] Modify `message_handler` in [`handlers.py`](ai_dev_bot_platform/app/telegram_bot/handlers.py)
   - Remove call to `orchestrator.process_user_request`
   - Add logic to create unique project directory
   - Write user message to `app_description.md` in project directory

### (LOGIC) Refactor ModelOrchestrator to ProjectHelpers
2. [ ] Rename [`orchestrator_service.py`](ai_dev_bot_platform/app/services/orchestrator_service.py) to `project_helpers.py`
3. [ ] Rename `ModelOrchestrator` class to `ProjectHelpers`
4. [ ] Delete `process_user_request` method
5. [ ] Refactor helper methods to be stateless functions

### (LOGIC) Create CLI for Roo Agent Integration
6. [ ] Create new file [`cli_runner.py`](ai_dev_bot_platform/cli_runner.py)
7. [ ] Implement CLI using argparse/click
8. [ ] Add commands: 
   - `generate-plan`
   - `implement-task`
   - `deduct-credits`

### (LOGIC) Update Roo Rules to Use CLI
9. [ ] Update rules in [`.roo/rules-planner.md`](.roo/rules-planner.md)
10. [ ] Update rules in [`.roo/rules-developer.md`](.roo/rules-developer.md)
11. [ ] Replace complex logic with CLI calls