# Phase 1: Foundational Asynchronous Overhaul Implementation Guide

## Goal
Decouple the user-facing Telegram bot from long-running build processes. The bot will only kick-start autonomous workflows and receive status updates, not block on task completion.

## Implementation Steps

### 1. Create Asynchronous Task Queue
- **File:** `ai_dev_bot_platform/app/services/task_queue.py`
- **Implementation:**
  ```python
  import asyncio
  from collections import deque
  from typing import Callable, Coroutine, Any
  
  class TaskQueue:
      def __init__(self):
          self._queue = deque()
          self._is_processing = False
          
      async def add_task(self, task: Callable[[], Coroutine[Any, Any, None]]):
          self._queue.append(task)
          if not self._is_processing:
              self._process_tasks()
              
      async def _process_tasks(self):
          self._is_processing = True
          while self._queue:
              task = self._queue.popleft()
              await task()
          self._is_processing = False
  ```

### 2. Modify Orchestrator to Use Task Queue
- **File:** `ai_dev_bot_platform/app/services/orchestrator_service.py`
- **Changes:**
  ```python
  # Add to imports
  from app.services.task_queue import TaskQueue
  
  class ModelOrchestrator:
      def __init__(self, db: Session):
          # ... existing code ...
          self.task_queue = TaskQueue()
  
      async def process_user_request(self, user: User, user_input: str) -> dict:
          # ... existing code ...
  
          # For long-running tasks, add to queue instead of executing directly
          if self._is_long_running(user_input):
              await self.task_queue.add_task(
                  lambda: self._handle_task_async(user, user_input)
              )
              return {
                  "text": "Your request has been queued. You'll receive updates when processing starts.",
                  "zip_buffer": None
              }
          # ... handle other requests synchronously ...
  
      async def _handle_task_async(self, user: User, user_input: str):
          # Actual task processing logic
          # ... similar to existing process_user_request but with status updates ...
  ```

### 3. Add Status Notification System
- **File:** `ai_dev_bot_platform/app/services/notification_service.py`
- **Implementation:**
  ```python
  from telegram import Bot
  from app.core.config import settings
  
  class NotificationService:
      def __init__(self):
          self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
      
      async def send_update(self, chat_id: int, message: str):
          await self.bot.send_message(chat_id=chat_id, text=message)
  ```

### 4. Integrate Notifications with Orchestrator
- **File:** `ai_dev_bot_platform/app/services/orchestrator_service.py`
- **Changes:**
  ```python
  # Add to imports
  from app.services.notification_service import NotificationService
  
  class ModelOrchestrator:
      def __init__(self, db: Session):
          # ... existing code ...
          self.notifier = NotificationService()
  
      async def _handle_task_async(self, user: User, user_input: str):
          try:
              await self.notifier.send_update(user.telegram_user_id, "🚀 Processing started...")
              # ... processing logic ...
              await self.notifier.send_update(user.telegram_user_id, "✅ Processing completed!")
          except Exception as e:
              await self.notifier.send_update(user.telegram_user_id, f"❌ Processing failed: {str(e)}")
  ```

### 5. Update Telegram Handlers
- **File:** `ai_dev_bot_platform/app/telegram_bot/handlers.py`
- **Changes:**
  ```python
  async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
      # ... existing code ...
      
      # Remove long-running acknowledgment messages
      # if is_new_project_description(text):
      #   await update.message.reply_text("Thanks! I'm analyzing...")
      # elif text.lower().strip().startswith("implement task"):
      #   await update.message.reply_text("Got it. Working on that task now...")
      
      # Instead, just queue the task
      response_data = await orchestrator.process_user_request(user_db, text)
      # ... rest of existing code ...
  ```

## Verification Steps
1. After implementation, send a project description to the bot
2. Verify immediate response: "Your request has been queued..."
3. Verify subsequent status updates arrive as processing progresses
4. Confirm final results are delivered without blocking the bot interface