---
status: "open"
priority: "medium"
---

# Task: Simplify Telegram Interface and Deprecate Old Orchestrator Logic

## Description
Now that the autonomous agent factory is fully operational via `run_autonomy.py`, the original Telegram bot interface and `ModelOrchestrator` service contain complex, now-obsolete logic. The bot's role should be simplified to being just a "work intake" mechanism.

## Acceptance Criteria
1.  The `telegram_bot/handlers.py` `message_handler` function must be refactored. Its only responsibility should be to take the user's text and create a new markdown file in the `work_items/` directory (e.g., `work_items/item-XXX-user-request.md`) with a status of "open".
2.  All complex `_handle_...` methods in `ai_dev_bot_platform/app/services/orchestrator_service.py` (e.g., `_handle_new_project`, `_handle_implement_task`, `_handle_refine_request`) must be removed. The class itself may be removed if no longer needed.
3.  Telegram UI elements like inline buttons for "Implement Task" must be removed from `handlers.py`, as the new autonomous loop handles task progression automatically.
4.  The user should receive a simple confirmation message like: "Your request has been received and will be processed. I will notify you upon completion."