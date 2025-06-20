# Plan 009: Audit Fixes Implementation

This plan addresses critical issues identified in the audit failure report (work_items/item-005-audit-failure.md).

## 1. Agent Responsibility and Workflow Correction

### Task 1.1: Remove README Generation from Implementer Agent
- [x] **File to Modify:** `ai_dev_bot_platform/app/agents/implementer_agent.py`
- [x] **Action:** Remove the block of code responsible for calling `ReadmeGenerationService`, writing `README.md`, and committing it in the `run_tdd_cycle` method.
- [x] **Rationale:** README generation should be handled by Architect after all implementation is complete.

### Task 1.2: Refactor Implementer Agent's TDD Logic
- **File to Modify:** `ai_dev_bot_platform/app/agents/implementer_agent.py`
- **Action:** Refactor `run_tdd_cycle` and `implement_todo_item` methods to only return a dictionary with `filename` and `code`. Remove git commit and signal creation logic.
- **Output:** The method should return: `{"filename": filename, "code": code}`

### Task 1.3: Correct Orchestrator's Implementation Flow
- **File to Modify:** `ai_dev_bot_platform/app/services/orchestrator_service.py`
- **Actions:**
  1. Update `_handle_implement_task` to call the refactored `implement_todo_item`
  2. Save generated file using `storage_service.upload_file` and `project_file_service`
  3. Call `architect_agent.verify_implementation_step`
  4. On verification APPROVED:
     - Update `current_todo_markdown` to mark task as `[x]`
     - Commit changes to version control
     - Proceed to next task or completion

## 2. Database Schema Mismatches

### Task 2.1: Implement Conversations Table
- **Files:**
  - Model: `ai_dev_bot_platform/app/models/conversation_model.py`
  - Migration: New Alembic migration
- **Actions:**
  1. Verify Conversation model has all required fields
  2. Generate migration: `alembic revision --autogenerate -m "Add conversations table"`
  3. Inspect migration file in `versions/` for `op.create_table('conversations')`
  4. Apply migration: `alembic upgrade head`

### Task 2.2: Implement API Keys Table
- **Files:**
  - Model: `ai_dev_bot_platform/app/models/api_key_models.py`
  - Service: `ai_dev_bot_platform/app/services/api_key_manager.py`
  - Migration: New Alembic migration
- **Actions:**
  1. Create `api_keys` model with fields: `provider`, `encrypted_key`, `is_active`, `last_used`, `usage_count`
  2. Generate migration: `alembic revision --autogenerate -m "Add api_keys table"`
  3. Refactor `APIKeyManager` to use database instead of environment variables

## 3. Requirement Gathering Flow

### Task 3.1: Trigger Requirement Gathering from /start
- **File to Modify:** `ai_dev_bot_platform/app/telegram_bot/handlers.py`
- **Action:** Update `start_command` to call `start_requirement_gathering(update, context)`

### Task 3.2: Implement State-Based Routing
- **File to Modify:** `ai_dev_bot_platform/app/telegram_bot/handlers.py`
- **Action:** Refactor `message_handler` to:
  1. Check `is_in_requirement_gathering(context)`
  2. If true, route to appropriate handler based on current state
  3. If false, proceed to Orchestrator logic

### Task 3.3: Handoff to Orchestrator After Confirmation
- **File to Modify:** `ai_dev_bot_platform/app/telegram_bot/requirement_gathering.py`
- **Action:** Update `handle_confirmation` to:
  1. Create project in database
  2. Pass confirmed project description to Orchestrator

## Acceptance Criteria
- ImplementerAgent no longer generates README
- Orchestrator handles all code saving, TODO updates and verification
- README generated only at project completion
- Conversations and API keys tables exist with migrations
- APIKeyManager uses database
- Requirement gathering flow works end-to-end
- State-based routing handles all requirement gathering states