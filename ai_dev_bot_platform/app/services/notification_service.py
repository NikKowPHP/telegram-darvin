from telegram import Bot
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    async def send_update(self, chat_id: int, message: str):
        try:
            await self.bot.send_message(chat_id=chat_id, text=message)
            logger.info(f"Sent notification to {chat_id}: {message}")
        except Exception as e:
            logger.error(f"Failed to send notification to {chat_id}: {e}")
