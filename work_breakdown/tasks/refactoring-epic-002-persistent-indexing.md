# Implement Persistent Codebase Indexing

## Tasks

### (LOGIC) Execute Existing Refactor Plan
1. [ ] Configure Celery Application
   - Create [`celery_app.py`](ai_dev_bot_platform/app/background_tasks/celery_app.py)
   - Implement Celery instance with Redis broker/backend

2. [ ] Create Telegram Notification Utility
   - Implement [`bot_utils.py`](ai_dev_bot_platform/app/telegram_bot/bot_utils.py)
   - Add `send_telegram_message` function

3. [ ] Define Main Celery Task
   - Create [`tasks.py`](ai_dev_bot_platform/app/background_tasks/tasks.py)
   - Implement `process_user_request_task`

4. [ ] Update Telegram Handler
   - Modify [`handlers.py`](ai_dev_bot_platform/app/telegram_bot/handlers.py)
   - Replace message_handler with job dispatching logic

5. [ ] Document Celery Worker
   - Update [`README.md`](README.md)
   - Add worker startup instructions

### (LOGIC) Implement pgvector Migration
6. [ ] Update Dependencies
   - Modify [`requirements.txt`](ai_dev_bot_platform/requirements.txt)
   - Add pgvector, remove FAISS dependencies

7. [ ] Create Embedding Model
   - Create [`embedding.py`](ai_dev_bot_platform/app/models/embedding.py)
   - Define ProjectEmbedding table schema

8. [ ] Refactor CodebaseIndexingService
   - Update [`codebase_indexing_service.py`](ai_dev_bot_platform/app/services/codebase_indexing_service.py)
   - Replace FAISS with pgvector implementation

9. [ ] Update Orchestrator
   - Modify [`orchestrator_service.py`](ai_dev_bot_platform/app/services/orchestrator_service.py)
   - Pass db session to indexer calls

10. [ ] Document Supabase Setup
    - Update [`README.md`](README.md)
    - Add pgvector extension instructions
    - Add embedding service setup