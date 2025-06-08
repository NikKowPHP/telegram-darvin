import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from app.core.config import settings
from app.telegram_bot.handlers import start_command, help_command, message_handler

logger = logging.getLogger(__name__)

def run_bot():
    logger.info("Starting Telegram bot...")
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    # Add more command handlers here

    # Register message handler for non-command messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    logger.info("Telegram bot polling...")
    application.run_polling()

if __name__ == "__main__":
    # This is for running the bot directly (e.g., for development)
    # In production, this might be managed by a process manager or part of the FastAPI app startup.
    from app.core.logging_config import setup_logging
    setup_logging()
    run_bot()