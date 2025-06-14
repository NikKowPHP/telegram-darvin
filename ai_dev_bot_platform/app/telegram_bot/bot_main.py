import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from app.core.config import settings
from app.telegram_bot.handlers import (
    start_command,
    help_command,
    credits_command,
    message_handler,
    button_handler,
)

logger = logging.getLogger(__name__)


async def run_bot():
    """Initializes and runs the Telegram bot."""
    logger.info("Building Telegram application...")
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("credits", credits_command))

    # Register message and button handlers
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler)
    )
    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Initializing Telegram bot application...")
    await application.initialize()
    logger.info("Starting Telegram bot polling...")
    await application.start()
    await application.updater.start_polling()
    logger.info("Telegram bot is now running.")
