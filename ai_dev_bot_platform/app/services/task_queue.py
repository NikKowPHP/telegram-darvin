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
            asyncio.create_task(self._process_tasks())
            
    async def _process_tasks(self):
        self._is_processing = True
        while self._queue:
            task = self._queue.popleft()
            try:
                await task()
            except Exception as e:
                print(f"Task failed with error: {str(e)}")
        self._is_processing = False